import streamlit as st
from query import handle_query  # Import the query handler function
from Chat import Chat  # Import the Chat class (make sure it's defined in chat.py)
from openai import OpenAI


OPENAI_API_KEY = st.secrets["openai"]["API_KEY"]


st.title("Advanced Chatbot")

# Initialize chat instances in session state if not already initialized
if "chats" not in st.session_state:
    openai_client = OpenAI(api_key=st.secrets["openai"]["API_KEY"])
    assistant = openai_client.beta.assistants.retrieve("asst_H8RXmor1XBDG0F1917fixtHE")
    assistant_id = assistant.id

    st.session_state.chats = {"chat_1": Chat()}

# Sidebar for selecting chat instances
chat_id = st.sidebar.selectbox("Select Chat Instance", options=list(st.session_state.chats.keys()))

# Display the selected chat's history
for message in st.session_state.chats[chat_id].get_history():
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Display the query count
st.write(f"Query count: {st.session_state.chats[chat_id].get_query_count()}")

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
    
# OpenAI Initialization
    openai_client = OpenAI(api_key=st.secrets["openai"]["API_KEY"])
    assistant = openai_client.beta.assistants.retrieve("asst_H8RXmor1XBDG0F1917fixtHE")
    assistant_id = assistant.id
    new_chat_id = f"chat_{len(st.session_state.chats) + 1}"
    st.session_state.chats[new_chat_id] = Chat(openai_client)  # Create a new Chat instance
    st.sidebar.selectbox("Select Chat Instance", options=list(st.session_state.chats.keys()))
