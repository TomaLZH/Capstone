import streamlit as st
from query import handle_query  # Import the query handler function
from Chat import Chat  # Import the Chat class (make sure it's defined in chat.py)
from openai import OpenAI

# OpenAI Initialization
OPENAI_API_KEY = st.secrets["openai"]["API_KEY"]
openai_client = OpenAI(api_key=OPENAI_API_KEY)
it_skill_level= "Beginner"

# App title
st.title("Chatbot")
# Function to update the skill level when the dropdown changes
def update_skill_level():
    # Store the updated skill level in session state
    st.session_state.it_skill_level = it_skill_level
    chat_instance.set_skill_level(it_skill_level)


# Initialize session state for chat instances
if "chats" not in st.session_state:
    st.session_state.chats = {"chat_1": Chat(openai_client)}
    st.session_state.selected_chat_id = "chat_1"  # Default selected chat

# Sidebar for creating and displaying chats
st.sidebar.header("Chat Instances")

# Display all chats as buttons in the sidebar
for chat_id in st.session_state.chats.keys():
    if st.sidebar.button(f"{chat_id}"):
        st.session_state.selected_chat_id = chat_id  # Update the selected chat

# Button to create a new chat instance
if st.sidebar.button("New Chat"):
    new_chat_id = f"Chat_{len(st.session_state.chats) + 1}"
    st.session_state.chats[new_chat_id] = Chat(openai_client)
    st.session_state.selected_chat_id = new_chat_id  # Automatically switch to the new chat


# Display message history for the selected chat
chat_instance = st.session_state.chats[st.session_state.selected_chat_id]


# Introduction Section: Ask the user to select their company configuration and IT skill level
st.subheader("Company Configuration and IT Skill Level")
st.title("SKILL:" + chat_instance.get_skill_level())


# Dropdown for Company Configuration
company_config = st.selectbox(
    "Select your company's configuration:",
    ["Small Business", "Medium Business", "Large Business", "Enterprise"],
    help="Choose the company configuration that best describes your organization."
)


# Dropdown for IT Skill Level
it_skill_level = st.selectbox(
    "Select your IT skill level:",
    ["Beginner", "Intermediate", "Advanced", "Expert"],
    help="Choose the IT skill level that best represents your team's expertise.",
    on_change = update_skill_level()
)

st.subheader(f"{st.session_state.selected_chat_id}")
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
