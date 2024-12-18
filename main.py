import streamlit as st
from query import handle_query  # Import the query handler function
from Chat import Chat  # Import the Chat class (make sure it's defined in chat.py)
from openai import OpenAI

# OpenAI Initialization
OPENAI_API_KEY = st.secrets["openai"]["API_KEY"]
openai_client = OpenAI(api_key=OPENAI_API_KEY)

# App title
st.title("Chatbot")

# Initialize session state for chat instances
if "chats" not in st.session_state:
    st.session_state.chats = {"chat_1": Chat(openai_client)}
    st.session_state.selected_chat_id = "chat_1"  # Default selected chat

# Sidebar for selecting or creating a new chat instance
chat_id = st.sidebar.selectbox(
    "Select Chat Instance",
    options=list(st.session_state.chats.keys()),
    index=list(st.session_state.chats.keys()).index(st.session_state.selected_chat_id)
)

if st.sidebar.button("New Chat"):
    # Create a new empty chat instance
    new_chat_id = f"chat_{len(st.session_state.chats) + 1}"
    st.session_state.chats[new_chat_id] = Chat(openai_client)
    st.session_state.selected_chat_id = new_chat_id  # Update the selected chat

# Update selected chat_id in session state
st.session_state.selected_chat_id = chat_id

# Display message history for the selected chat
chat_instance = st.session_state.chats[st.session_state.selected_chat_id]
for message in chat_instance.get_history():
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("How can I assist you today?"):
    # Display the user message
    st.chat_message("user").markdown(prompt)
    chat_instance.add_message({"role": "user", "content": prompt})

    # Call the query handler
    with st.spinner("Thinking..."):
        response = handle_query(prompt, chat_instance)  # Pass the selected chat instance

    # Display the assistant's response
    st.chat_message("assistant").markdown(response)
    chat_instance.add_message({"role": "assistant", "content": response})
