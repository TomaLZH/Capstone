import streamlit as st
from sentence_transformers import SentenceTransformer
from sentence_transformers.cross_encoder import CrossEncoder
from openai import OpenAI
from pymilvus import MilvusClient

# Load API keys from Streamlit secrets
OPENAI_API_KEY = st.secrets["openai"]["API_KEY"]

conn = st.connection("postgresql", type="sql")

# Initialize bi-encoder model for query embedding
bi_encoder = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")

# Initialize cross-encoder model for re-ranking query and context
cross_encoder = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

# Initialize Milvus vector database client
client = MilvusClient(uri=st.secrets["milvus"]["url"],
                      token=st.secrets["milvus"]["token"])

client.describe_collection(collection_name="Capstone")

# Initialize OpenAI client
openai_client = OpenAI(api_key=OPENAI_API_KEY)
assistant = openai_client.beta.assistants.retrieve(
    "asst_H8RXmor1XBDG0F1917fixtHE")


def get_resources():
    return conn, bi_encoder, cross_encoder, client, openai_client, assistant
