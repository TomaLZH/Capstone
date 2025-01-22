from Initialize import get_resources
import numpy as np
import logging
from Chat import Chat
import streamlit as st

# Load models and resources such as encoders, database collections, and OpenAI client
bi_encoder, cross_encoder, client, openai_client, assistant = get_resources()


def handle_query(query, chat: Chat):

    # #Check if any Clause or Domain is mentioned in the query
    system_message_for_Clause = """
    You are an assistant that processes queries to determine their intent and extract information. Follow these steps:
    
    1. Check if the query is about editing company information. If so, respond with "Editing Company Information", if not proceed to the next step.

    2. Identify whether a query mentions a domain number, clause number, or "Risk Ref" number strictly in the following 2 formats:
    - B.(number).(optional clause number) (for domains or clauses)
    - Risk Ref: (number) (for Risk Ref references)
        
    What is the Domain, Clause, or Risk Ref mentioned in the query: What is B.1.1?
    B.1.1
    What is the Domain, Clause, or Risk Ref mentioned in the query: What is B.12?
    B.12.
    What is the Domain, Clause, or Risk Ref mentioned in the query: How do I implement B.1.5?
    B.1.5
    What is the Domain, Clause, or Risk Ref mentioned in the query: What is Cyber Trust Mark?
    None
    What is the Domain, Clause, or Risk Ref mentioned in the query: What is the purpose of Cyber Trust Mark?
    None
    What is the Domain, Clause, or Risk Ref mentioned in the query: What are the clauses in B.9 for supporter tier?
    B.9.
    What is the Domain, Clause, or Risk Ref mentioned in the query: What are the clauses in B.15?
    B.15.
    What is the Domain, Clause, or Risk Ref mentioned in the query: What is risk ref 3?
    Risk Ref: 3
    What is the Domain, Clause, or Risk Ref mentioned in the query: What is Risk Reference 21?
    Risk Ref: 21
    What is the Domain, Clause, or Risk Ref mentioned in the query: How do I handle Risk Ref 5 in my implementation?
    Risk Ref: 5
    What is the Domain, Clause, or Risk Ref mentioned in the query: Hello?
    None

    If no domain number, clause number, or Risk Ref number is found in user's query, respond with "None".
    """

    # Construct the user message containing conversation history and the query
    DomainClause = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": system_message_for_Clause},
                  {"role": "user", "content": query}]
    )

    # #If no clause or domain is mentioned
    if DomainClause.choices[0].message.content == "None":

        # Define the system message to guide the assistant's behavior
        system_message = """
        You are an AI assistant tasked with reformulating user queries to improve retrieval in a RAG (Retrieval-Augmented Generation) system. Follow this two-step process:
        1) Determine Clarity: First, analyze whether the user query makes sense on its own. If it is clear and self-contained, return it as is without modification.
        2) Enhance Using Context: If the query is ambiguous, incomplete, or dependent on prior chat history for clarity, rewrite it to incorporate necessary details from the chat history. Ensure the reformulated query maintains the user's intent while retrieving the most accurate and relevant information.
        """
        # Construct the user message containing conversation history and the query
        user_message = f"Conversation so far:\n{chat.get_history()}\n\nOriginal Query: {query}\n\n Rewritten Query:"

        # Use OpenAI GPT to process the query based on the system message
        completion = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": system_message},
                      {"role": "user", "content": user_message}]
        )
        st.write(
            f"Semantic Search Term = {completion.choices[0].message.content}")

        # Extract the processed query from the GPT completion response
        processed_query = completion.choices[0].message.content

        # Generate an embedding for the processed query using the bi-encoder
        query_embedding = bi_encoder.encode(processed_query).astype(np.float32)
        # Normalize the embedding
        query_embedding /= np.linalg.norm(query_embedding)

        # Search the collection using the query embedding to find relevant documents

        results = client.search(
            collection_name="Capstone",
            anns_field="vector",
            top_k=20,
            data=[query_embedding],
            output_fields=["text"],
        )

        top_passages = [item['entity']['text'] for item in results[0]]
        # Create input pairs for the cross-encoder by combining the query with each passage
        cross_inp = [[query, passage] for passage in top_passages]
    # If domain or clause is mentioned

    elif DomainClause.choices[0].message.content.startswith("Editing Company Information"):
        system_message = """
            You are an assistant that help edit company information based on the user query.
            Respond with the edited company information without changing the structure or any other information apart from the requested changes.
        """

        # Construct the user message containing conversation history and the query
        user_message = f"Original Company Information: {chat.get_infrastructure()}\n\nUser Query: {query}"
        completion = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": system_message},
                      {"role": "user", "content": user_message}]
        )
        chat.set_infrastructure(completion.choices[0].message.content)
        return "Your company information has been updated successfully."

    else:
        # Embed the domain or clause mentioned in the query
        st.write(
            f"Lexicon Search Term = {DomainClause.choices[0].message.content}")
        results = client.query(
            collection_name="Capstone",
            filter=f"text like '%{DomainClause.choices[0].message.content}%'",
            top_k=20,
            output_fields=["text"]
        )

        # Extract text passages from the results for further processing
        top_passages = [doc['text'] for doc in results]
        # Create input pairs for the cross-encoder by combining the query with each passage
        cross_inp = [[query, passage] for passage in top_passages]

    if results:
        # Predict relevance scores for each pair using the cross-encoder
        cross_scores = cross_encoder.predict(cross_inp)

        # Filter results to only include those with a score > 0
        filtered_results = [
            (passage, score) for passage, score in zip(top_passages, cross_scores) if score > 0
        ]

        # Sort the results by their relevance scores in descending order and select the top 15
        sorted_results = sorted(
            filtered_results, key=lambda x: x[1], reverse=True)[:15]

        # Construct the context from the top-ranked passages
        context = "\n\n\n".join(
            [f"Passage: {r[0]}\nRelevance Score: {r[1]:.2f}" for r in sorted_results]) or "none found"
        
        st.write(f"Context = {context}")

        # Send the refined query and context to OpenAI for further processing
        openai_client.beta.threads.messages.create(
            thread_id=chat.get_thread_id(),  # Retrieve the thread ID from the chat instance
            role="user",
            content=f"Background Information: {context}\n\nCompany Information: {chat.get_infrastructure()}\n\nUser Query: {query}\n",
        )

        # Execute and poll the assistant's response from OpenAI
        run = openai_client.beta.threads.runs.create_and_poll(
            thread_id=chat.get_thread_id(),
            assistant_id=assistant.id,
        )

        # Retrieve the latest messages from the thread
        messages = openai_client.beta.threads.messages.list(
            thread_id=chat.get_thread_id())

        # Extract the assistant's response from the messages
        response = messages.data[0].content[0].text.value

        return response
    else:
        # Return a message if no relevant results are found
        return "No relevant results found."
