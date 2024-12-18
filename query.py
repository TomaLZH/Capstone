from Initialize import get_resources
import numpy as np
import logging
from Chat import Chat
import streamlit as st



# Load models and resources
bi_encoder, cross_encoder, collection, openai_client, assistant = get_resources()

def handle_query(query, chat: Chat):
    # Prepare system message
    system_message = """
    You are an assistant analyzing the conversation. If the user query is clear and unambiguous, return the query as-is.
    If the query is ambiguous, generate a focused query. If no context can be determined, return the query as-is. Do not replace 'ref' with 'reference'.
    """

    user_message = f"Conversation so far:\n{chat.get_history()}\n\nUser Query: {query}"

    # Call OpenAI GPT
    completion = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": system_message},
                  {"role": "user", "content": user_message}]
    )
    processed_query = completion.choices[0].message.content
    print(processed_query)
    logging.info(f"Processed query: {processed_query}")
    # Embed query and search
    query_embedding = bi_encoder.encode(processed_query).astype(np.float32)
    query_embedding /= np.linalg.norm(query_embedding)

    results = list(collection.find(sort={"$vector": query_embedding}, limit=50, include_similarity=True))

    if results:
        # Use cross-encoder for re-ranking
        top_passages = [doc['text'] for doc in results]
        cross_inp = [[processed_query, passage] for passage in top_passages]
        cross_scores = cross_encoder.predict(cross_inp)

        # Filter and sort results
        sorted_results = sorted(
            zip(top_passages, cross_scores),
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        context = "\n\n\n".join([r[0] for r in sorted_results]) or "none found"
        # Send refined query and context to OpenAI
        
        openai_client.beta.threads.messages.create(
            thread_id=chat.get_thread_id(),  # Correct method call to get thread ID
            role="user",
            content=f"User's skill level: {chat.get_skill_level()}.\n User's IT Infrastructure Environment: {chat.get_environment()}.\n\n Context: {context}\n\nFull Query: {query}\n",
        )
        run = openai_client.beta.threads.runs.create_and_poll(
            thread_id=chat.get_thread_id(), 
            assistant_id=assistant.id,
        )
        messages = openai_client.beta.threads.messages.list(thread_id=chat.get_thread_id())
        response = messages.data[0].content[0].text.value
        
        return response
    else:
        return "No relevant results found."
    
