import streamlit as st
from query import handle_query  # Import the query handler function
from Chat import Chat  # Import the Chat class
from openai import OpenAI
from Initialize import get_resources
import pandas as pd
from functions import analyze_file
import json
import random
from databasefunctions import authenticate_user


# Load required resources and models
conn, cur, bi_encoder, cross_encoder, collection, openai_client, assistant = get_resources()

# # App title
# st.title("Cyber Trust Mark Assistant")
# Function to update the skill level when the dropdown changes


def update_skill_level():
    # Update the skill level in the chat instance when the session state changes
    chat_instance.set_skill_level(st.session_state.it_skill_level)


# Initialize session state for login pop-up
if "show_login" not in st.session_state:
    st.session_state.show_login = False
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = None

# Function to toggle login pop-up


def toggle_login():
    st.session_state.show_login = not st.session_state.show_login


# Top-right login button (using columns to position)
col1, col2 = st.columns([8, 1])
with col2:
    if st.button("🔑 Login"):
        toggle_login()

# Display login pop-up if button is clicked
if st.session_state.show_login:
    with st.sidebar:  # Simulating a pop-up
        st.write("### Login / Register")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Submit"):
            result = authenticate_user(username, password)

            if result["status"] == 200:  # Login successful
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.show_login = False
                st.sidebar.success(f"✅ Logged in as {username}")
                st.rerun()

            elif result["status"] == 201:  # New user registered
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.show_login = False
                st.sidebar.success(
                    f"🎉 Account created! Logged in as {username}")
                st.rerun()

            else:  # Invalid password
                st.error(result["message"])

# Display logged-in user info
if st.session_state.logged_in:
    st.sidebar.write(f"👤 Logged in as **{st.session_state.username}**")


# Initialize session state for chat instances and user preferences
if "chats" not in st.session_state:
    # Create a dictionary to store multiple chat instances
    st.session_state.chats = {"chat_1": Chat(openai_client)}
    # Set the default selected chat instance
    st.session_state.selected_chat_id = "chat_1"

if "it_skill_level" not in st.session_state:
    # Set the default IT skill level to Beginner
    st.session_state.it_skill_level = "Beginner"

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
    st.rerun()

# Retrieve the selected chat instance
chat_instance = st.session_state.chats[st.session_state.selected_chat_id]

st.subheader("Company Configuration and IT Skill Level")
st.write("Selected IT Skill Level:", chat_instance.get_skill_level())
st.write("Upload Company Details: ")

# File uploader for company details
uploaded_file = st.file_uploader("Choose a file", type=[
                                 "csv", "xlsx", "docx"], help="Upload your company details file.")

if uploaded_file is not None:
    # Check if the file has already been processed
    if "uploaded_file_name" not in st.session_state or st.session_state.uploaded_file_name != uploaded_file.name:
        # Process the uploaded file
        file_details = {"filename": uploaded_file.name,
                        "filetype": uploaded_file.type, "filesize": uploaded_file.size}
        st.write(file_details)
        # Analyze the file and store the results in session state
        st.session_state.analyzed_file_data = analyze_file(
            chat_instance, uploaded_file)
        st.session_state.uploaded_file_name = uploaded_file.name

    # Display analyzed data or results
    st.write("File Analysis Results:")
    st.write(chat_instance.get_infrastructure())

# Display the checklist for the selected chat instance
checklist = chat_instance.get_checklist()
# Convert the string to a dictionary
if checklist:
    checklist_dict = json.loads(checklist)
    # Extracting the title and the domains
    checklist_title = checklist_dict['checklist_title']
    domains = checklist_dict['Domains']

    # Display the title
    st.write(f"### {checklist_title}")

    # Loop through the domains and display the clauses as a checklist
    for domain, clauses in domains.items():
        st.write(f"#### {domain}")
        for clause in clauses:
            st.write(f"- [ ] {clause}")


# Dropdown for selecting the IT skill level
it_skill_level = st.selectbox(
    "Select your IT skill level:",
    ["Beginner", "Advanced"],
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

# List of possible prompts to randomly choose from
prompts = [
    "How do I implement Domain B.7 for Advocate tier?",
    "Would you like to learn about Domain B.8?",
    "Tell me about your implementation of B.7?",
    "What help do you need for Domain B.9?",
    "What documents are needed for the Cyber Trust Mark?",
    "What is Risk Ref 9",
    "What is the Cyber Trust Mark?",
    "Give me an filled example of Risk Ref 18",
    "What are all the Clauses in Domain B.22?",
]

# Randomly select a prompt
prompt = random.choice(prompts)


# Handle user input and assistant responses
if prompt := st.chat_input("What is Risk Ref 9"):
    # Display the user's input in the chat interface
    st.chat_message("user").markdown(prompt)
    chat_instance.add_message({"role": "user", "content": prompt})

    # Call the query handler to process the user input
    with st.spinner("Thinking..."):
        # Pass the selected chat instance to the handler
        response = handle_query(prompt, chat_instance)

    # Display the assistant's response
    st.chat_message("assistant").markdown(response)
    chat_instance.add_message({"role": "assistant", "content": response})
    st.rerun()
