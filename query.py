from Initialize import get_resources
import numpy as np
import logging
from Chat import Chat
import streamlit as st

# Load models and resources such as encoders, database collections, and OpenAI client
bi_encoder, cross_encoder, collection, openai_client, assistant = get_resources()

def handle_query(query, chat: Chat):
    # Define the system message to guide the assistant's behavior
    system_message = """
    You are an assistant analyzing the conversation. If the user query is clear and unambiguous, return the query as-is.
    If the query is ambiguous, generate a focused query. If no context can be determined, return the query as-is. Do not replace 'ref' with 'reference'.
    """

    # Construct the user message containing conversation history and the query
    user_message = f"Conversation so far:\n{chat.get_history()}\n\nUser Query: {query}"

    # Use OpenAI GPT to process the query based on the system message
    completion = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": system_message},
                  {"role": "user", "content": user_message}]
    )

    # Extract the processed query from the GPT completion response
    processed_query = completion.choices[0].message.content
    print(processed_query)  # Debugging/logging output
    logging.info(f"Processed query: {processed_query}")

    # Generate an embedding for the processed query using the bi-encoder
    query_embedding = bi_encoder.encode(processed_query).astype(np.float32)
    query_embedding /= np.linalg.norm(query_embedding)  # Normalize the embedding

    # Search the collection using the query embedding to find relevant documents
    results = list(collection.find(sort={"$vector": query_embedding}, limit=50, include_similarity=True))

    if results:
        # Extract text passages from the results for further processing
        top_passages = [doc['text'] for doc in results]

        # Create input pairs for the cross-encoder by combining the query with each passage
        cross_inp = [[processed_query, passage] for passage in top_passages]

        # Predict relevance scores for each pair using the cross-encoder
        cross_scores = cross_encoder.predict(cross_inp)

        # Sort the results by their relevance scores in descending order and select the top 15
        sorted_results = sorted(
            zip(top_passages, cross_scores),
            key=lambda x: x[1],
            reverse=True
        )[:15]

        # Construct the context from the top-ranked passages
        context = "\n\n\n".join([f"Passage: {r[0]}\nRelevance Score: {r[1]:.2f}" for r in sorted_results]) or "none found"
        return context
        # Send the refined query and context to OpenAI for further processing
        openai_client.beta.threads.messages.create(
            thread_id=chat.get_thread_id(),  # Retrieve the thread ID from the chat instance
            role="user",
            content=f"User's skill level: {chat.get_skill_level()}.\n User's IT Infrastructure Environment: {chat.get_environment()}.\n\n Context: {context}\n\nUser Query: {query}\n",
        )

        # Execute and poll the assistant's response from OpenAI
        run = openai_client.beta.threads.runs.create_and_poll(
            thread_id=chat.get_thread_id(), 
            assistant_id=assistant.id,
        )

        # Retrieve the latest messages from the thread
        messages = openai_client.beta.threads.messages.list(thread_id=chat.get_thread_id())

        # Extract the assistant's response from the messages
        response = messages.data[0].content[0].text.value

        return response
    else:
        # Return a message if no relevant results are found
        return "No relevant results found."
