import re
import pdfplumber
from langchain.schema import Document
import pandas as pd
from transformers import AutoTokenizer
from sentence_transformers import SentenceTransformer


# Read Huawei dataset called output.xlsx
data = pd.read_excel("output.xlsx")

# Extract the text from excel, as headers: values and chunk based on per row
# Extract the text from Excel, ensuring max length of 2000 characters
all_chunks = []
for index, row in data.iterrows():
    row_text = " | ".join([f"{col}: {str(row[col])}" for col in data.columns if pd.notna(row[col])])
    row_text = row_text[:2000]  # Truncate if longer than 2000 characters
    all_chunks.append(row_text)


#Upload the chunks to Milvus after embedding
model = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")


# Encode all chunks
embeddings = model.encode(all_chunks, normalize_embeddings=True)


"""# Connection of Milvus"""

from pymilvus import MilvusClient

client = MilvusClient(uri="https://in03-6d0166dfffa8e21ddd.serverless.gcp-us-west1.cloud.zilliz.com", token="ac9e06ae092afb90f90b61de112607cb2918fbba386dfc45edba79c7a39639ef9c3abdfd45b2522d7699c5b12e7e6c8638fcc794")

client.describe_collection(collection_name="Capstone")

"""# Insertion of Data"""

# Prepare the documents in the required format
documents = [{"text": chunk, "vector": embedding.tolist()} for chunk, embedding in zip(all_chunks, embeddings)]

 
res = client.insert(
    collection_name="Capstone",
    data=documents,
    ids=None,
    wait=True
)
