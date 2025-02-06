import streamlit as st
from sentence_transformers import SentenceTransformer
from sentence_transformers.cross_encoder import CrossEncoder
from openai import OpenAI
from pymilvus import MilvusClient

# Load API keys from Streamlit secrets
OPENAI_API_KEY = st.secrets["openai"]["API_KEY"]

st.connection("postgresql", type="sql")

# Initialize bi-encoder model for query embedding
bi_encoder = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")

# Initialize cross-encoder model for re-ranking query and context
cross_encoder = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

# Initialize Milvus vector database client
client = MilvusClient(uri="https://in03-6d0166da8e21ddd.serverless.gcp-us-west1.cloud.zilliz.com",
                      token="ac9e06ae092afb90f90b61de112607cb2918fbba386dfc45edba79c7a39639ef9c3abdfd45b2522d7699c5b12e7e6c8638fcc794")

client.describe_collection(collection_name="Capstone")

# Initialize OpenAI client
openai_client = OpenAI(api_key=OPENAI_API_KEY)
assistant = openai_client.beta.assistants.retrieve("asst_H8RXmor1XBDG0F1917fixtHE")

def get_resources():
    return bi_encoder, cross_encoder, client, openai_client, assistant
