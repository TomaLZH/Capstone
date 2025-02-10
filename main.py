import streamlit as st
from query import handle_query  # Import the query handler function
from Chat import Chat  # Import the Chat class
from openai import OpenAI
from Initialize import get_resources
import pandas as pd
import json
from functions import analyze_file
import pickle
from databasefunctions import authenticate_user
import random

# Load required resources and models
conn, bi_encoder, cross_encoder, collection, openai_client, assistant = get_resources()

# Initialize session state for login
if "show_login" not in st.session_state:
    st.session_state.show_login = False
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = None

# Function to toggle login pop-up
def toggle_login():
    st.session_state.show_login = not st.session_state.show_login

# Top-right login button
col1, col2 = st.columns([8, 1])
with col2:
    if st.button("🔑 Login"):
        toggle_login()

# Display login pop-up
if st.session_state.show_login:
    with st.sidebar:
        st.write("### Login / Register")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Submit"):
            result = authenticate_user(username, password)
            if result["status"] in [200, 201]:  # Login or new user registered
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.show_login = False
                st.rerun()
            else:
                st.error(result["message"])

# Display logged-in user info
if st.session_state.logged_in:
    st.sidebar.write(f"👤 Logged in as **{st.session_state.username}**")

# Initialize single chat instance
if "chat_instance" not in st.session_state:
    st.session_state.chat_instance = Chat(openai_client)
chat_instance = st.session_state.chat_instance

# Set IT skill level
if "it_skill_level" not in st.session_state:
    st.session_state.it_skill_level = "Beginner"

def update_skill_level():
    chat_instance.set_skill_level(st.session_state.it_skill_level)

# UI for IT skill level selection
st.subheader("Company Configuration and IT Skill Level")
st.selectbox(
    "Select your IT skill level:",
    ["Beginner", "Advanced"],
    key="it_skill_level",
    on_change=update_skill_level
)

# File uploader
st.write("Upload Company Details:")
uploaded_file = st.file_uploader("Choose a file", type=["csv", "xlsx", "docx"])
if uploaded_file and ("uploaded_file_name" not in st.session_state or st.session_state.uploaded_file_name != uploaded_file.name):
    st.session_state.analyzed_file_data = analyze_file(chat_instance, uploaded_file)
    st.session_state.uploaded_file_name = uploaded_file.name

# Display checklist
checklist = chat_instance.get_checklist()
if checklist:
    checklist_dict = json.loads(checklist)
    st.write(f"### {checklist_dict['checklist_title']}")
    for domain, clauses in checklist_dict['Domains'].items():
        st.write(f"#### {domain}")
        for clause in clauses:
            st.write(f"- [ ] {clause}")

# Display chat history
st.subheader("Chat")
for message in chat_instance.get_history():
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Random prompt selection
prompts = [
    "How do I implement Domain B.7 for Advocate tier?",
    "Would you like to learn about Domain B.8?",
    "Tell me about your implementation of B.7?",
    "What help do you need for Domain B.9?",
    "What documents are needed for the Cyber Trust Mark?",
    "What is Risk Ref 9",
    "What is the Cyber Trust Mark?",
    "Give me a filled example of Risk Ref 18",
    "What are all the Clauses in Domain B.22?",
]
prompt = random.choice(prompts)

# Handle user input
if prompt := st.chat_input("What is Risk Ref 9"):
    st.chat_message("user").markdown(prompt)
    chat_instance.add_message({"role": "user", "content": prompt})
    with st.spinner("Thinking..."):
        response = handle_query(prompt, chat_instance)
    st.chat_message("assistant").markdown(response)
    chat_instance.add_message({"role": "assistant", "content": response})
    st.rerun()