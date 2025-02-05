import os
from google.cloud import secretmanager
from google.cloud.sql.connector import Connector, IPTypes
import pg8000
import sqlalchemy
from sqlalchemy import create_engine
from sentence_transformers import SentenceTransformer
from sentence_transformers.cross_encoder import CrossEncoder
from openai import OpenAI
import streamlit as st
from pymilvus import MilvusClient


def access_secret_version(project_id, secret_id, version_id="latest"):
    """Access a secret version from Google Secret Manager."""
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")


# Fetch Google Application Credentials JSON from Secret Manager
project_id = "626097532017"
secret_id = "SQLStuff"
google_credentials_path = "/tmp/gcp_credentials.json"

# Write secret content to a temporary file
with open(google_credentials_path, "w") as f:
    f.write(access_secret_version(project_id, secret_id))

# Set the environment variable for Google credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = google_credentials_path


def connect_with_connector() -> sqlalchemy.engine.base.Engine:
    """
    Initializes a connection pool for a Cloud SQL instance of PostgreSQL.
    Uses the Cloud SQL Python Connector.
    """
    instance_connection_name = "ardent-kite-449907-q5:us-central1:capstone"
    db_user = "ZH"
    db_pass = "password"  # Secure this properly
    db_name = "postgres"

    ip_type = IPTypes.PRIVATE if os.environ.get(
        "PRIVATE_IP") else IPTypes.PUBLIC
    connector = Connector()

    def getconn() -> pg8000.dbapi.Connection:
        return connector.connect(
            instance_connection_name,
            "pg8000",
            user=db_user,
            password=db_pass,
            db=db_name,
            ip_type=ip_type,
        )

    return sqlalchemy.create_engine(
        "postgresql+pg8000://",
        creator=getconn,
    )


# Initialize database engine
engine = connect_with_connector()

# Load API keys from Streamlit secrets
OPENAI_API_KEY = st.secrets["openai"]["API_KEY"]

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
assistant = openai_client.beta.assistants.retrieve(
    "asst_H8RXmor1XBDG0F1917fixtHE")


def get_resources():
    return engine, bi_encoder, cross_encoder, client, openai_client, assistant
