# src/initialize.py
from astrapy import DataAPIClient
from sentence_transformers import SentenceTransformer
from sentence_transformers.cross_encoder import CrossEncoder
from openai import OpenAI
from dotenv import load_dotenv
import os
import streamlit as st

OPENAI_API_KEY = st.secrets["openai"]["API_KEY"]
ASTRA_API_KEY = st.secrets["astradb"]["API_KEY"]
ASTRA_DB_URL = st.secrets["astradb"]["DB_URL"]


# Models Initialization
bi_encoder = SentenceTransformer("sentence-transformers/multi-qa-mpnet-base-cos-v1")
cross_encoder = CrossEncoder("sentence-transformers/ms-marco-MiniLM-L6-v2")


client = DataAPIClient(ASTRA_API_KEY)
db = client.get_database_by_api_endpoint(ASTRA_DB_URL)
collection = db.get_collection("Capstone")

print(f"Connected to Astra DB: {db.list_collection_names()}")

# OpenAI Initialization
openai_client = OpenAI(api_key=OPENAI_API_KEY)
assistant = openai_client.beta.assistants.retrieve("asst_H8RXmor1XBDG0F1917fixtHE")

# Exported Initialization
def get_resources():
    return bi_encoder, cross_encoder, collection, openai_client, assistant
