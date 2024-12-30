# src/initialize.py
from astrapy import DataAPIClient
from sentence_transformers import SentenceTransformer
from sentence_transformers.cross_encoder import CrossEncoder
from openai import OpenAI
from dotenv import load_dotenv
import os
import streamlit as st

# Load API keys and configurations from Streamlit secrets
OPENAI_API_KEY = st.secrets["openai"]["API_KEY"]
ASTRA_API_KEY = st.secrets["astradb"]["API_KEY"]
ASTRA_DB_URL = st.secrets["astradb"]["DB_URL"]

# Initialize bi-encoder model for query embedding
# This model is used to create embeddings for text similarity
# bi_encoder = SentenceTransformer("sentence-transformers/multi-qa-mpnet-base-cos-v1")
# Alternate model option (commented out):
bi_encoder = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")

# Initialize cross-encoder model for re-ranking query and context
# This model is used to refine search results based on relevance
# cross_encoder = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
# Alternate Model option (commented out):
cross_encoder = CrossEncoder(""BAAI/bge-reranker-v2-m3")

# Initialize Astra database client for managing collections
client = DataAPIClient(ASTRA_API_KEY)
db = client.get_database_by_api_endpoint(ASTRA_DB_URL)
collection = db.get_collection("Capstone")

# Log the connected database collections
print(f"Connected to Astra DB: {db.list_collection_names()}")

# Initialize OpenAI client for generating assistant responses
openai_client = OpenAI(api_key=OPENAI_API_KEY)
# Retrieve the assistant instance from OpenAI
assistant = openai_client.beta.assistants.retrieve("asst_H8RXmor1XBDG0F1917fixtHE")

# Function to export initialized resources
# This function returns all initialized models and clients for use in the application
def get_resources():
    return bi_encoder, cross_encoder, collection, openai_client, assistant
