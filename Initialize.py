# src/initialize.py
from sentence_transformers import SentenceTransformer
from sentence_transformers.cross_encoder import CrossEncoder
from openai import OpenAI
from dotenv import load_dotenv
import os
import streamlit as st
from pymilvus import MilvusClient
import sqlite3

conn = sqlite3.connect("sqlite3.db")
cur = con.cursor()

# Load API keys and configurations from Streamlit secrets
OPENAI_API_KEY = st.secrets["openai"]["API_KEY"]

# Initialize bi-encoder model for query embedding
# This model is used to create embeddings for text similarity
# bi_encoder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
# Alternate model option (commented out):
bi_encoder = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")

# Initialize cross-encoder model for re-ranking query and context
# This model is used to refine search results based on relevance
cross_encoder = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
# Alternate Model option (commented out):
# cross_encoder = CrossEncoder("BAAI/bge-reranker-v2-m3")


# Log the connected database collections
client = MilvusClient(uri="https://in03-6d0166da8e21ddd.serverless.gcp-us-west1.cloud.zilliz.com",
                      token="ac9e06ae092afb90f90b61de112607cb2918fbba386dfc45edba79c7a39639ef9c3abdfd45b2522d7699c5b12e7e6c8638fcc794")

client.describe_collection(collection_name="Capstone")


# Initialize OpenAI client for generating assistant responses
openai_client = OpenAI(api_key=OPENAI_API_KEY)
# Retrieve the assistant instance from OpenAI
assistant = openai_client.beta.assistants.retrieve(
    "asst_H8RXmor1XBDG0F1917fixtHE")

# Function to export initialized resources
# This function returns all initialized models and clients for use in the application


def get_resources():
    return conn, cur, bi_encoder, cross_encoder, client, openai_client, assistant
