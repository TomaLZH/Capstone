from Initialize import get_resources
import numpy as np
import logging
from Chat import Chat
import streamlit as st

# Load models and resources such as encoders, database collections, and OpenAI client
engine, bi_encoder, cross_encoder, client, openai_client, assistant = get_resources()


def extract_domain_clause_or_risk_ref(query):
    system_message_for_Clause = """
        You are an assistant that processes queries to determine their intent and extract information. Follow these steps strictly:

        1. Check if the query is about editing company information. If so, respond with "Editing Company Information" and stop, without proceeding to the next steps.

        2. Identify whether a query mentions a tier, domain number, clause number, or "Risk Ref" number strictly in the following formats:
            - B.(number).(optional clause number) (for domains or clauses)
            - Risk Ref: (number) (for Risk Ref references)

            **If any domain number, clause number, or Risk Ref number is found, return it immediately and do not proceed to any further steps.**

        3. If no domain number, clause number, or Risk Ref number is found in the user's query, identify whether the query mentions a preparedness tier (Supporter, Practitioner, Promoter, Performer, Advocate). 
            - If found, return the extracted tier.
            
        4. If the query does not contain any of the above information, return "None".

        **Examples:**
        Query: What is the Domain, Clause, or Risk Ref mentioned in the query: What is B.1.1?
        B.1.1

        Query: What is the Domain, Clause, or Risk Ref mentioned in the query: What is B.12?
        B.12.

        Query: What is the Domain, Clause, or Risk Ref mentioned in the query: What is the purpose of Cyber Trust Mark?
        None

        Query: What is the Domain, Clause, or Risk Ref mentioned in the query: What is Risk Ref 3?
        Risk Ref: 3

        Query: What is the Domain, Clause, or Risk Ref mentioned in the query: What are all the clauses for advocate tier?
        Advocate

        Query: What is the Domain, Clause, or Risk Ref mentioned in the query: Hello?
        None

        Query: What is the Domain, Clause, or Risk Ref mentioned in the query: What do i do for B.4 for supporter tier?
        B.4.

    """

    # Send query for classification
    DomainClause = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": system_message_for_Clause},
                  {"role": "user", "content": query}]
    )

    return DomainClause.choices[0].message.content


def reformulate_query(query, chat):
    """ Reformulate the query using the conversation history if necessary. """
    system_message = """
    You are an AI assistant tasked with reformulating user queries to improve retrieval in a RAG (Retrieval-Augmented Generation) system. Follow this two-step process:
    1) Determine Clarity: First, analyze whether the user query makes sense on its own. If it is clear and self-contained, return it as is without modification.
    2) Enhance Using Context: If the query is ambiguous, incomplete, or dependent on prior chat history for clarity, rewrite it to incorporate necessary details from the chat history. Ensure the reformulated query maintains the user's intent while retrieving the most accurate and relevant information.
    """

    user_message = f"Conversation so far:\n{chat.get_history()}\n\nOriginal Query: {query}\n\n Rewritten Query:"

    # Request OpenAI to reformulate the query
    completion = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": system_message},
                  {"role": "user", "content": user_message}]
    )

    return completion.choices[0].message.content


def search_and_retrieve_results(query_embedding):
    """ Perform the search and retrieve results based on the query embedding. """
    results = client.search(
        collection_name="Capstone",
        anns_field="vector",
        top_k=20,
        data=[query_embedding],
        output_fields=["text"],
    )

    top_passages = [item['entity']['text'] for item in results[0]]
    return top_passages


def handle_edit_company_info(query, chat):
    """ Handle the query for editing company information. """
    system_message = """
    You are an assistant that helps edit company information based on the user query.
    Respond with the edited company information without changing the structure or any other information apart from the requested changes.
    """

    user_message = f"Original Company Information: {chat.get_infrastructure()}\n\nUser Query: {query}"

    completion = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": system_message},
                  {"role": "user", "content": user_message}]
    )

    chat.set_infrastructure(completion.choices[0].message.content)
    return "Your company information has been updated successfully."


def predict_relevance_and_filter_results(query, top_passages):
    """ Predict relevance scores for the results and filter based on relevance. """
    cross_inp = [[query, passage] for passage in top_passages]
    cross_scores = cross_encoder.predict(cross_inp)

    filtered_results = [
        (passage, score) for passage, score in zip(top_passages, cross_scores) if score > 0
    ]

    sorted_results = sorted(
        filtered_results, key=lambda x: x[1], reverse=True)[:15]
    return sorted_results


def generate_checklist(query, chat):
    system_instruction = """
        You are an AI assistant that generates a checklist based on the user query. Follow these steps:

        1. **Analyze the user query** to identify the relevant Tier, Domains, or Clauses. If none are found, return "None". 
        2. **Generate a checklist** based on the information provided in the dataset below.  

        #### Dataset:  
        {
        "Domains": {
            "B.1 Governance": {
                "Promoter Tier": ["B.1.3"],
                "Performer Tier": ["B.1.4", "B.1.5", "B.1.6"],
                "Advocate Tier": ["B.1.7", "B.1.8"]
                },
            "B.2 Policies and Procedures": {
                "Promoter Tier": ["B.2.3"],
                "Performer Tier": ["B.2.4", "B.2.5", "B.2.6"],
                "Advocate Tier": ["B.2.7", "B.2.8", "B.2.9"]
                },
            "B.3 Risk Management": {
                "Supporter Tier": ["B.3.1", "B.3.2"],
                "Practitioner Tier": ["B.3.3", "B.3.4"],
                "Promoter Tier": ["B.3.5", "B.3.6"],
                "Performer Tier": ["B.3.7", "B.3.8", "B.3.9"],
                "Advocate Tier": ["B.3.10", "B.3.11", "B.3.12"]
                }
            "B.4 Cyber Strategy": {
                "Advocate Tier": ["B.4.5", "B.4.6", "B.4.7", "B.4.8", "B.4.9"]
                }
            "B.5 Compliance": {
                "Supporter Tier": ["B.5.1"],
                "Practitioner Tier": ["B.5.2"],
                "Promoter Tier": ["B.5.3", "B.5.4"],
                "Performer Tier": ["B.5.5", "B.5.6"],
                "Advocate Tier": ["B.5.7", "B.5.8", "B.5.9"]
                }
            "B.6 Audit": {
                "Performer Tier": ["B.6.4", "B.6.5", "B.6.6"],
                "Advocate Tier": ["B.6.7", "B.6.8"]
                }
            "B.7 Training and Awareness": {
                "Supporter Tier": ["B.7.1"],
                "Practitioner Tier": ["B.7.2", "B.7.3"],
                "Promoter Tier": ["B.7.4", "B.7.5"],
                "Performer Tier": ["B.7.6", "B.7.7", "B.7.8"],
                "Advocate Tier": ["B.7.9", "B.7.10", "B.7.11"]
                }
            "B.8 Asset Management": {
                "Supporter Tier": ["B.8.1"],
                "Practitioner Tier": ["B.8.2"],
                "Promoter Tier": ["B.8.3", "B.8.4", "B.8.5"],
                "Performer Tier": ["B.8.6", "B.8.7"],
                "Advocate Tier": ["B.8.8", "B.8.9", "B.8.10"]
                }
            "B.9 Data protection and privacy": {
                "Supporter Tier": ["B.9.1", "B.9.2", "B.9.3"],
                "Practitioner Tier": ["B.9.4"],
                "Promoter Tier": ["B.9.5", "B.9.6", "B.9.7"],
                "Performer Tier": ["B.9.8", "B.9.9", "B.9.10"],
                "Advocate Tier": ["B.9.11", "B.9.12", "B.9.13"]
                }
            "B.10 Backups": {
                "Supporter Tier": ["B.10.1"],
                "Practitioner Tier": ["B.10.2", "B.10.3"],
                "Promoter Tier": ["B.10.4", "B.10.5"],
                "Performer Tier": ["B.10.6", "B.10.7"],
                "Advocate Tier": ["B.10.8", "B.10.9", "B.10.10"]
                }
            "B.11 Bring YOur Own Device (BYOD)": {
                "Performer Tier": ["B.11.4"],
                "Advocate Tier": ["B.11.5", "B.11.6", "B.11.7"]
                }
            "B.12 System Security": {
                "Supporter Tier": ["B.12.1"],
                "Practitioner Tier": ["B.12.2", "B.12.3"],
                "Promoter Tier": ["B.12.4", "B.12.5", "B.12.6"],
                "Performer Tier": ["B.12.7", "B.12.8", "B.12.9", "B.12.10"],
                "Advocate Tier": ["B.12.11", "B.12.12", "B.12.13"]
                }
            "B.13 Antivirus/Antimalware": {
                "Supporter Tier": ["B.13.1"],
                "Practitioner Tier": ["B.13.2", "B.13.3", "B.13.4", "B.13.5"],
                "Promoter Tier": ["B.13.6"],
                "Performer Tier": ["B.13.7"],
                "Advocate Tier": ["B.13.8", "B.13.9", "B.13.10"]
                }
            "B.14 Secure Software Development Life Cycle": {
                "Advocate Tier": ["B.14.5", "B.14.6", "B.14.7", "B.14.8"]
                }
            "B.15 Access Control": {
                "Supporter Tier": ["B.15.1"],
                "Practitioner Tier": ["B.15.2", "B.15.3"],
                "Promoter Tier": ["B.15.4", "B.15.5", "B.15.6"],
                "Performer Tier": ["B.15.7", "B.15.8", "B.15.9"],
                "Advocate Tier": ["B.15.10", "B.15.11"]
                }
            "B.16 Cyber Threat Mangement": {
                "Performer Tier": ["B.16.4", "B.16.5", "B.16.6", "B.16.7", "B.16.8"],
                "Advocate Tier": ["B.16.9", "B.16.10", "B.16.11"]
                }
            "B.17 Third-party risk and oversight": {
                "Advocate Tier": ["B.17.5", "B.17.6", "B.17.7", "B.17.8", "B.17.9"]
                }
            "B.18 Vulnerability Assessment": {
                "Promoter Tier": ["B.18.3", "B.18.4"],
                "Performer Tier": ["B.18.5", "B.18.6", "B.18.7"],
                "Advocate Tier": ["B.18.8", "B.18.9", "B.18.10", "B.18.11"]
                }
            "B.19 Physical/Environmental Security": {
                "Practitioner Tier": ["B.19.2", "B.19.3", "B.19.4"],
                "Promoter Tier": ["B.19.5", "B.19.6", "B.19.7"],
                "Performer Tier": ["B.19.8", "B.19.9", "B.19.10"],
                "Advocate Tier": ["B.19.11", "B.19.12"]
                }
            "B.20 Network Security": {
                "Practitioner Tier": ["B.20.2", "B.20.3", "B.20.4"],
                "Promoter Tier": ["B.20.5", "B.20.6"],
                "Performer Tier": ["B.20.7", "B.20.8", "B.20.9"],
                "Advocate Tier": ["B.20.10", "B.20.11"]
                }
            "B.21 Incident Response": {
                "Supporter Tier": ["B.21.1"],
                "Practitioner Tier": ["B.21.2"],
                "Promoter Tier": ["B.21.3", "B.21.4"],
                "Performer Tier": ["B.21.5", "B.21.6"],
                "Advocate Tier": ["B.21.7", "B.21.8"]
                }
            "B.22 Business Continuity/Disaster recovery": {
                "Practitioner Tier": ["B.22.2"],
                "Promoter Tier": ["B.22.3", "B.22.4"],
                "Performer Tier": ["B.22.5", "B.22.6", "B.22.7", "B.22.8"],
                "Advocate Tier": ["B.22.9", "B.22.10"]
                }
            }
        }   
        3. **Respond based on query type**:
        - For a **specific clause query** (e.g., "What is B.1.1?"), return relevant clauses in the domain or tier most appropriate for the user's query.
        - For a **specific domain and tier query** (e.g., "What are the clauses in B.9 for supporter tier?"), return the relevant clauses for that tier within the domain.
        - For a **specific domain query** (e.g., "What are the clauses in B.15?"), return the clauses for all tiers within the domain.
        - For a **tier-wide query** (e.g., "What are all the clauses I need to implement for advocate tier?"), return the relevant clauses across all domains for that tier.
        - If no relevant information is found, return "None".

        #### Output Format:  
        {
        "checklist_title": "Clauses for Advocate Tier",
        "Domains": {
            "B.1 Governance": ["B.1.7", "B.1.8"],
            "B.2 Policies and Procedures": ["B.2.7", "B.2.8", "B.2.9"],
            ...
            }
        }


    """

    # Send the query for classification
    checklist = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": system_instruction},
                  {"role": "user", "content": query}]
    )

    return checklist.choices[0].message.content


def generate_final_response(sorted_results, query, chat):
    """ Combine context and query to generate the final response. """
    context_str = "\n\n\n".join(
        [f"Passage: {r[0]}\nRelevance Score: {r[1]:.2f}" for r in sorted_results]) or "none found"

    st.write(f"Context = {context_str}")

    openai_client.beta.threads.messages.create(
        thread_id=chat.get_thread_id(),  # Retrieve the thread ID from the chat instance
        role="user",
        content=f"Context: {context_str}\n\nCompany Information: {chat.get_infrastructure()}\n\nUser Skill level: {chat.get_skill_level()}\n\nUser Query: {query}\n",
    )

    # Execute and poll the assistant's response from OpenAI
    run = openai_client.beta.threads.runs.create_and_poll(
        thread_id=chat.get_thread_id(),
        assistant_id=assistant.id,
    )

    messages = openai_client.beta.threads.messages.list(
        thread_id=chat.get_thread_id())

    response = messages.data[0].content[0].text.value
    return response


def handle_query(query, chat: Chat):
    """ Main function to handle the query, split into smaller parts. """
    domain_clause = extract_domain_clause_or_risk_ref(query)

    if domain_clause == "None":
        processed_query = reformulate_query(query, chat)
        st.write(f"Reformulated Query = {processed_query}")
        query_embedding = bi_encoder.encode(processed_query).astype(np.float32)
        query_embedding /= np.linalg.norm(query_embedding)
        top_passages = search_and_retrieve_results(query_embedding)
        
    elif domain_clause.startswith("Editing Company Information"):
        return handle_edit_company_info(query, chat)

    else:
        # Embed the domain or clause mentioned in the query
        st.write(f"Lexicon Search Term = {domain_clause}")
        results = client.query(
            collection_name="Capstone",
            filter=f"text like '%{domain_clause}%'",
            output_fields=["text"]
        )
        chat.set_checklist(generate_checklist(query, chat))
        top_passages = [doc['text'] for doc in results]

    # Predict relevance and filter results
    sorted_results = predict_relevance_and_filter_results(query, top_passages)

    # Generate and return the final response
    return generate_final_response(sorted_results, query, chat)
