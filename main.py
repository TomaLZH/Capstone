import streamlit as st
from query import handle_query  # Import the query handler function

st.title("Advanced Chatbot")

# Initialize chat history in session state if not already initialized
if "messages" not in st.session_state:
    st.session_state.messages = {"chat_1": []}

# Sidebar for selecting chat instances
chat_id = st.sidebar.selectbox("Select Chat Instance", options=list(st.session_state.messages.keys()))

# Display the selected chat's history
for message in st.session_state.messages[chat_id]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("How can I assist you today?"):
    # Display the user message
    st.chat_message("user").markdown(prompt)
    st.session_state.messages[chat_id].append({"role": "user", "content": prompt})

    # Call the query handler
    with st.spinner("Thinking..."):
        response = handle_query(prompt)

    # Display the assistant's response
    st.chat_message("assistant").markdown(response)
    st.session_state.messages[chat_id].append({"role": "assistant", "content": response})

# Button to create a new chat instance
if st.sidebar.button("New Chat"):
    # Create a new empty chat instance
    new_chat_id = f"chat_{len(st.session_state.messages) + 1}"
    st.session_state.messages[new_chat_id] = []
    st.sidebar.selectbox("Select Chat Instance", options=list(st.session_state.messages.keys()))
