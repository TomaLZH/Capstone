import pandas as pd
from sentence_transformers import SentenceTransformer
from pymilvus import MilvusClient

# Function to load and process data from multiple Excel files
def load_and_process_excel(files):
    all_structured_data = []

    for excel_file in files:
        # Load the Excel file
        df = pd.read_excel(excel_file, sheet_name=None)  # Read all sheets

        # Extract data from each sheet
        for sheet_name, sheet_df in df.items():
            for index, row in sheet_df.iterrows():
                # Create a dictionary of column names and their values
                row_dict = {col: str(row[col]) if pd.notna(row[col]) else "" for col in sheet_df.columns}
                all_structured_data.append((sheet_name, row_dict))

    return all_structured_data

# Function to create a structured text from a sheet and row data
def create_structured_text(sheet_name, row_data):
    # Combine sheet name, column headers, and values
    context = f"Sheet: {sheet_name}. "
    context += " | ".join([f"{key}: {value}" for key, value in row_data.items()])
    return context

# Truncate text to a max length of 2000 characters
def truncate_text(data, max_length=2000):
    if isinstance(data, dict):
        if len(data["text"]) > max_length:
            print(f"Row with length {len(data['text'])} exceeds {max_length} characters.")
        data["text"] = data.get("text", "")[:max_length]  # Truncate the 'text' field if it's too long
    return data

# Load and process the Excel files
excel_files = ["output.xlsx"]  # Add all file paths
structured_data = load_and_process_excel(excel_files)

# Generate context-rich strings (structured text)
structured_texts = [create_structured_text(sheet_name, row) for sheet_name, row in structured_data]

# Load SentenceTransformer model for encoding
model = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")

# Encode all chunks
embeddings = model.encode(structured_texts, normalize_embeddings=True)

# Initialize Milvus client
client = MilvusClient(uri="https://in03-6d0166da8e21ddd.serverless.gcp-us-west1.cloud.zilliz.com", token="ac9e06ae092afb90f90b61de112607cb2918fbba386dfc45edba79c7a39639ef9c3abdfd45b2522d7699c5b12e7e6c8638fcc794")

client.describe_collection(collection_name="Capstone")

# Prepare the documents in the required format
documents = [{"text": chunk, "vector": embedding.tolist()} for chunk, embedding in zip(structured_texts, embeddings)]

# Truncate the text fields if necessary
documents = [truncate_text(doc) for doc in documents]

# Insert the documents into Milvus
try:
    res = client.insert(
        collection_name="Capstone",
        data=documents,
        ids=None,
        wait=True
    )
    print("Documents inserted successfully.")
except Exception as e:
    print(f"An error occurred during insertion: {e}")
