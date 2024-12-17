# query.py
from Initialize import get_resources
import numpy as np
from Chat import Chat

# Load models and resources
bi_encoder, cross_encoder, collection, openai_client, assistant, thread = get_resources()


def handle_query(query, chat, openai_client):
    # Prepare system message
    system_message = """
    You are an assistant analyzing the conversation. If the user query is clear and unambiguous, return the query as-is.
    If the query is ambiguous, generate a focused query. Do not replace 'ref' with 'reference'.
    """
    user_message = f"Conversation so far:\n{chat.get_history()}\n\nUser Query: {query}"

    # Call OpenAI GPT (using the specific thread ID for the selected chat)
    completion = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": system_message},
                  {"role": "user", "content": user_message}]
    )
    processed_query = completion.choices[0].message.content

    # Embed query and search as before...
    # Update chat history and send the response to the correct thread
    chat.add_message({"role": "system", "content": processed_query})

    # Use the thread for sending the full query and context
    openai_client.beta.threads.messages.create(
        thread_id=chat.get_thread_id(),
        role="user",
        content=f"Context: {processed_query}\nFull Query: {query}\n"
    )

    # Process the assistant's response...
    run = openai_client.beta.threads.runs.create_and_poll(thread_id=chat.get_thread_id(), assistant_id=assistant.id)
    messages = openai_client.beta.threads.messages.list(thread_id=chat.get_thread_id())
    response = messages.data[0].content[0].text.value

    chat.add_message({"role": "assistant", "content": response})
    return response
