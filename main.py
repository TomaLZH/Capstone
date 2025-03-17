import streamlit as st
from query import handle_query  # Import the query handler function
from Chat import Chat  # Import the Chat class
from openai import OpenAI
from Initialize import get_resources
import pandas as pd
import json
from functions import analyze_file
import pickle
from databasefunctions import authenticate_user, update_company_infrastructure, update_skilllevel, update_checklist
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
if "infrastructure" not in st.session_state:
    st.session_state.infrastructure = None
if "skill_level" not in st.session_state:
    st.session_state.skill_level = "Beginner"
if "check_list" not in st.session_state:
    st.session_state.check_list = None
if "checklist_state" not in st.session_state:
    st.session_state.checklist_state = {}

# Function to toggle login pop-up
def toggle_login():
    st.session_state.show_login = not st.session_state.show_login

# Function to handle logout
def logout():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

# Function to update checklist state
def update_checklist_state(domain, tier, index, value, clause):
    key = f"{domain}_{tier}_{index}"
    st.session_state.checklist_state[key] = {
        "checked": value,
        "clause": clause
    }
    
# Function to display checklist
def display_checklist(checklist):
    if not checklist or checklist == "None":
        st.info("No checklist available. Upload company details to generate a checklist.")
        return
        
    checklist_dict = json.loads(checklist)
    st.write(f"### {checklist_dict['checklist_title']}")

    for domain, tiers in checklist_dict['Domains'].items():
        st.write(f"#### {domain}")
        for tier, clauses in tiers.items():
            st.write(f"##### {tier}")
            for i, clause in enumerate(clauses):
                key = f"{domain}_{tier}_{i}"
                checked = st.checkbox(
                    clause, 
                    key=key,
                    value=st.session_state.checklist_state.get(key, {}).get("checked", False)
                )
                if checked != st.session_state.checklist_state.get(key, {}).get("checked", False):
                    update_checklist_state(domain, tier, i, checked, clause)

# Function to display chat history
def display_chat_history(chat_instance):
    st.subheader("Chat")
    if not chat_instance.get_history():
        st.info("No messages yet. Start a conversation!")
    else:
        for message in chat_instance.get_history():
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

# Function to handle chat input
def handle_chat_input(chat_instance):
    prompt = st.chat_input("Ask about cybersecurity controls...")
    if prompt:
        if len(prompt.strip()) < 2:
            st.warning("Please enter a valid question.")
            return
            
        st.chat_message("user").markdown(prompt)
        chat_instance.add_message({"role": "user", "content": prompt})
        try:
            with st.spinner("Thinking..."):
                response = handle_query(prompt, chat_instance)
            st.chat_message("assistant").markdown(response)
            chat_instance.add_message({"role": "assistant", "content": response})
        except Exception as e:
            st.error(f"Error processing your request: {str(e)}")
        finally:
            st.rerun()

# Top-right login button
col1, col2 = st.columns([8, 1])
with col2:
    if st.session_state.logged_in:
        if st.button("🔓 Logout"):
            logout()
    else:
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
                st.session_state.infrastructure = result["user"][3]
                st.session_state.skill_level = result["user"][5]
                st.session_state.check_list = result["user"][4]

                # Initialize chat instance
                st.session_state.chat_instance = Chat(openai_client)
                chat_instance = st.session_state.chat_instance
                chat_instance.set_skill_level(st.session_state.skill_level)
                chat_instance.set_infrastructure(
                    st.session_state.infrastructure)
                chat_instance.set_checklist(st.session_state.check_list)
                chat_instance.set_username(st.session_state.username)
                st.rerun()
            else:
                st.error(result["message"])

# Display logged-in user info
if st.session_state.logged_in:
    st.sidebar.write(f"👤 Logged in as **{st.session_state.username}**")
    st.sidebar.write(f"🏢 Company: **{st.session_state.infrastructure}**")
    st.sidebar.write(f"🎓 Skill Level: **{st.session_state.skill_level}**")

# Initialize single chat instance
if "chat_instance" not in st.session_state:
    st.session_state.chat_instance = Chat(openai_client)
chat_instance = st.session_state.chat_instance

# Set IT skill level
if "it_skill_level" not in st.session_state:
    st.session_state.it_skill_level = "Beginner"

def update_skill_level():
    chat_instance.set_skill_level(st.session_state.it_skill_level)
    # If logged in, update database
    if st.session_state.logged_in:
        update_skilllevel(st.session_state.username,
                          st.session_state.it_skill_level)

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
    try:
        with st.spinner("Analyzing file..."):
            st.session_state.analyzed_file_data = analyze_file(
                chat_instance, uploaded_file)
            st.session_state.uploaded_file_name = uploaded_file.name
            # if logged in, update database
            if st.session_state.logged_in:
                update_company_infrastructure(
                    st.session_state.username, chat_instance.get_infrastructure())
        st.success("File analyzed successfully!")
        st.rerun()
    except Exception as e:
        st.error(f"Error analyzing file: {str(e)}")

# Display interactive checklist
display_checklist(chat_instance.get_checklist())

# Display chat interface
display_chat_history(chat_instance)
handle_chat_input(chat_instance)