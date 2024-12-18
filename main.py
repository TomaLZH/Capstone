import streamlit as st
from query import handle_query  # Import the query handler function
from Chat import Chat  # Import the Chat class (make sure it's defined in chat.py)
from openai import OpenAI

# OpenAI Initialization
OPENAI_API_KEY = st.secrets["openai"]["API_KEY"]
openai_client = OpenAI(api_key=OPENAI_API_KEY)

# App title
st.title("Cyber Trust Mark Assistant")

# Function to update the skill level when the dropdown changes
def update_skill_level():
    # Get the selected chat instance
    chat_instance_id = st.session_state.selected_chat_id
    # Update the skill level for the selected chat instance
    chat_instance = st.session_state.chats[chat_instance_id]
    chat_instance.set_skill_level(st.session_state.it_skill_level[chat_instance_id])

# Initialize session state for chat instances and skill level
if "chats" not in st.session_state:
    st.session_state.chats = {"chat_1": Chat(openai_client)}
    st.session_state.selected_chat_id = "chat_1"  # Default selected chat

# Initialize IT skill level for each chat instance
if "it_skill_level" not in st.session_state:
    st.session_state.it_skill_level = {"chat_1": "Beginner"}  # Default value for IT skill level for the first chat

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
    # Set default IT skill level for the new chat
    st.session_state.it_skill_level[new_chat_id] = "Beginner"
    st.session_state.selected_chat_id = new_chat_id  # Automatically switch to the new chat

# Display message history for the selected chat
chat_instance = st.session_state.chats[st.session_state.selected_chat_id]

# Introduction Section: Ask the user to select their company configuration and IT skill level
st.subheader("Company Configuration and IT Skill Level")
st.title(f"SKILL: {st.session_state.it_skill_level[st.session_state.selected_chat_id]}")


# Dropdown for IT Skill Level
it_skill_level = st.selectbox(
    "Select your IT skill level:",
    ["Beginner", "Intermediate", "Advanced", "Expert"],
    help="Choose the IT skill level that best represents your team's expertise.",
    key=f"it_skill_level_{st.session_state.selected_chat_id}",  # Unique key per chat
    on_change=update_skill_level  # Directly update the class instance
)

# After the selection, we update the class immediately after session state is modified
# Display current chat messages
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
