# src/initialize.py
from astrapy import DataAPIClient
from sentence_transformers import SentenceTransformer
from sentence_transformers.cross_encoder import CrossEncoder
from openai import OpenAI

# Models Initialization
bi_encoder = SentenceTransformer("Local_bi_encoder")
cross_encoder = CrossEncoder("Local_cross_encoder")

# AstraDB Initialization
ASTRA_API_KEY = "AstraCS:fkZlYRRXBuIsirXCAkpdZPzh:391988e0eb5a8cad152e0b308cfb7bf9b6c6b918bf178ad82ab17d3ffa805385"
ASTRA_DB_URL = "https://dd4da96d-4f77-4989-8109-5d70fa690131-us-east-2.apps.astra.datastax.com"

client = DataAPIClient(ASTRA_API_KEY)
db = client.get_database_by_api_endpoint(ASTRA_DB_URL)
collection = db.get_collection("Capstone")

print(f"Connected to Astra DB: {db.list_collection_names()}")

# OpenAI Initialization
OPENAI_API_KEY = "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"
openai_client = OpenAI(api_key=OPENAI_API_KEY)
assistant = openai_client.beta.assistants.retrieve("asst_H8RXmor1XBDG0F1917fixtHE")
thread = openai_client.beta.threads.create()

# Exported Initialization
def get_resources():
    return bi_encoder, cross_encoder, collection, openai_client, assistant, thread
