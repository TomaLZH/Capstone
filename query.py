from Initialize import get_resources
import numpy as np
import logging
from Chat import Chat
import streamlit as st

# Load models and resources such as encoders, database collections, and OpenAI client
bi_encoder, cross_encoder, client, openai_client, assistant = get_resources()


def extract_domain_clause_or_risk_ref(query):
    """ Extract domain, clause, or risk ref from the query. """
    system_message_for_Clause = """
    You are an assistant that processes queries to determine their intent and extract information. Follow these steps:
    
    1. Check if the query is about editing company information. If so, respond with "Editing Company Information", if not proceed to the next step.

    2. Identify whether a query mentions a domain number, clause number, or "Risk Ref" number strictly in the following 2 formats:
    - B.(number).(optional clause number) (for domains or clauses)
    - Risk Ref: (number) (for Risk Ref references)
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


def generate_final_response(sorted_results, query, chat):
    """ Combine context and query to generate the final response. """
    context_str = "\n\n\n".join(
        [f"Passage: {r[0]}\nRelevance Score: {r[1]:.2f}" for r in sorted_results]) or "none found"

    st.write(f"Context = {context_str}")

    openai_client.beta.threads.messages.create(
        thread_id=chat.get_thread_id(),  # Retrieve the thread ID from the chat instance
        role="user",
        content=f"Background Information: {context_str}\n\nCompany Information: {chat.get_infrastructure()}\n\nUser Query: {query}\n",
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
            top_k=20,
            output_fields=["text"]
        )

        top_passages = [doc['text'] for doc in results]

    # Predict relevance and filter results
    sorted_results = predict_relevance_and_filter_results(query, top_passages)

    # Generate and return the final response
    return generate_final_response(sorted_results, query, chat)
