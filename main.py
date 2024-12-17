import streamlit as st
from query import handle_query  # Import the query handler function
from Chat import Chat  # Import the Chat class (make sure it's defined in chat.py)
from openai import OpenAI

# API Key from Streamlit secrets
OPENAI_API_KEY = st.secrets["openai"]["API_KEY"]

st.title("Advanced Chatbot")

# Initialize OpenAI client and assistant if not already initialized
if "openai_client" not in st.session_state:
    openai_client = OpenAI(api_key=OPENAI_API_KEY)
    assistant = openai_client.beta.assistants.retrieve("asst_H8RXmor1XBDG0F1917fixtHE")
    assistant_id = assistant.id
    st.session_state.openai_client = openai_client
    st.session_state.assistant = assistant
    st.session_state.assistant_id = assistant_id
    st.session_state.chats = {"chat_1": Chat(openai_client)}

# Sidebar for selecting chat instances
chat_id = st.sidebar.selectbox("Select Chat Instance", options=list(st.session_state.chats.keys()))

# Display the selected chat's history
for message in st.session_state.chats[chat_id].get_history():
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("How can I assist you today?"):
    # Display the user message
    st.chat_message("user").markdown(prompt)
    st.session_state.chats[chat_id].add_message({"role": "user", "content": prompt})

    # Call the query handler
    with st.spinner("Thinking..."):
        response = handle_query(prompt, st.session_state.chats[chat_id])  # Pass the chat instance

    # Display the assistant's response
    st.chat_message("assistant").markdown(response)
    st.session_state.chats[chat_id].add_message({"role": "assistant", "content": response})

# Button to create a new chat instance
if st.sidebar.button("New Chat"):
    # Create a new empty chat instance
    new_chat_id = f"chat_{len(st.session_state.chats) + 1}"
    st.session_state.chats[new_chat_id] = Chat(st.session_state.openai_client)  # Create a new Chat instance

    # Refresh the chat instance selection
    st.sidebar.selectbox("Select Chat Instance", options=list(st.session_state.chats.keys()))
