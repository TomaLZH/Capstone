import streamlit as st
from query import handle_query  # Import the query handler function
from Chat import Chat  # Import the Chat class 
from openai import OpenAI
from Initialize import get_resources

# Load required resources and models
bi_encoder, cross_encoder, collection, openai_client, assistant = get_resources()

# App title
st.title("Cyber Trust Mark Assistant")

# Function to update the skill level when the dropdown changes
def update_skill_level():
    # Update the skill level in the chat instance when the session state changes
    chat_instance.set_skill_level(st.session_state.it_skill_level)
    
# Function to update the company environment when the dropdown changes
def update_environment():
    # Update the environment in the chat instance when the session state changes
    chat_instance.set_environment(st.session_state.environment)

# Initialize session state for chat instances and user preferences
if "chats" not in st.session_state:
    # Create a dictionary to store multiple chat instances
    st.session_state.chats = {"chat_1": Chat(openai_client)}
    st.session_state.selected_chat_id = "chat_1"  # Set the default selected chat instance

if "it_skill_level" not in st.session_state:
    # Set the default IT skill level to Beginner
    st.session_state.it_skill_level = "Beginner"

if "environment" not in st.session_state:
    # Set the default environment to None Selected
    st.session_state.environment = "None Selected"

# Sidebar for managing chat instances
st.sidebar.header("Chat Instances")

# Display each chat instance as a button in the sidebar
for chat_id in st.session_state.chats.keys():
    if st.sidebar.button(f"{chat_id}"):
        # Switch to the selected chat instance
        st.session_state.selected_chat_id = chat_id
        
# Button to create a new chat instance
if st.sidebar.button("New Chat"):
    # Create a new chat instance with a unique ID
    new_chat_id = f"Chat_{len(st.session_state.chats) + 1}"
    st.session_state.chats[new_chat_id] = Chat(openai_client)
    st.session_state.selected_chat_id = new_chat_id  # Switch to the new chat instance

# Retrieve the selected chat instance
chat_instance = st.session_state.chats[st.session_state.selected_chat_id]

# Introduction Section: Display and allow configuration of company environment and IT skill level
st.subheader("Company Configuration and IT Skill Level")
# Show the selected environment and skill level
st.write("Selected Company Environment:", chat_instance.get_environment())
st.write("Selected IT Skill Level:", chat_instance.get_skill_level())

# Dropdown for selecting the company's environment
environment = st.selectbox(
    "Select your company's environment:",
    ["None Selected", "On-premises", "Cloud-based", "Hybrid"],
    help="Choose the environment that best describes your organization.",
    key="environment",  # Bind this dropdown to session_state
    on_change=update_environment  # Update the chat instance when changed
)

# Dropdown for selecting the IT skill level
it_skill_level = st.selectbox(
    "Select your IT skill level:",
    ["Beginner", "Intermediate", "Advanced"],
    help="Choose the IT skill level that best represents your team's expertise.",
    key="it_skill_level",  # Bind this dropdown to session_state
    on_change=update_skill_level  # Update the chat instance when changed
)

# Display the chat messages for the selected chat instance
st.subheader(f"{st.session_state.selected_chat_id}")
for message in chat_instance.get_history():
    # Display each message in the chat history
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Handle user input and assistant responses
if prompt := st.chat_input("How can I assist you today?"):
    # Display the user's input in the chat interface
    st.chat_message("user").markdown(prompt)
    chat_instance.add_message({"role": "user", "content": prompt})

    # Call the query handler to process the user input
    with st.spinner("Thinking..."):
        response = handle_query(prompt, chat_instance)  # Pass the selected chat instance to the handler

    # Display the assistant's response
    st.chat_message("assistant").markdown(response)
    chat_instance.add_message({"role": "assistant", "content": response})
