import re
import pdfplumber
from langchain.schema import Document
import pandas as pd
from transformers import AutoTokenizer

# tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/multi-qa-mpnet-base-cos-v1")
tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-mpnet-base-v2")

# Function to extract text and tables from a PDF file
def extract_text_and_tables_from_pdf(pdf_path):
    text = ""
    table_texts = []

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            # Extract text from each page
            page_text = page.extract_text()
            if page_text:
                text += page_text

            # Extract tables from each page
            tables = page.extract_tables()
            for idx, table in enumerate(tables):
                # Convert to DataFrame
                table_df = pd.DataFrame(table)

                # Remove empty columns and rows
                table_df.dropna(how="all", inplace=True)
                table_df.dropna(axis=1, how="all", inplace=True)

                # Check if table has content after cleaning
                if not table_df.empty:
                    # Use the first row as header if applicable
                    if table_df.shape[0] > 0 and all(pd.notna(table_df.iloc[0])):
                        table_df.columns = table_df.iloc[0]
                        table_df = table_df[1:]

                    # Convert DataFrame to a formatted string and label
                    table_str = table_df.to_string(index=False, header=True)
                    table_texts.append(f"Table {idx + 1}:\n{table_str}\n")

    return text, "\n".join(table_texts)

def clean_text(text):
    # Improve regex cleaning to be more specific
    text = re.sub(r'cybersecurity certification cyber trust mark', '', text, flags=re.IGNORECASE)
    text = re.sub(r'copyright', '', text, flags=re.IGNORECASE)
    text = re.sub(r'[^a-zA-Z0-9\s.,!?\'"@]', '', text)  # Clean up special characters
    text = re.sub(r"[ \t]*\n+[ \t]*", "\n", text)  # Replace extra newlines
    text = re.sub(r'none', '', text)  # Remove the word 'none'
    text = text.strip()
    text = re.sub(r"\n{2,}", "\n", text)  # Remove multiple consecutive newlines
    text = re.sub(r'\bCSA Cybersecurity Certification Cyber Trust mark\b', '', text, flags=re.IGNORECASE)  # Remove the title
    # You could add more specific cleaning here depending on known patterns
    return text

def chunk_text(text, max_tokens=512, overlap_tokens=128):
    # List to hold the chunks of text
    chunked_texts = []
    start = 0
    text_length = len(text)
    # While there's still text to process
    while start < text_length:
        # Determine the end of the window
        end = start + max_tokens
        # Take the slice of text from 'start' to 'end'
        chunk = text[start:end]
        # Tokenize this chunk
        tokens = tokenizer.encode(chunk)
        # If the tokenized chunk is too long, adjust
        while len(tokens) > max_tokens:
            end -= 1
            chunk = text[start:end]
            tokens = tokenizer.encode(chunk)
        # If the tokenized chunk is too short, merge it with the next chunk
        if len(tokens) < max_tokens and start + max_tokens < text_length:
            next_chunk = text[start + max_tokens:start + 2 * max_tokens]
            next_tokens = tokenizer.encode(next_chunk)
            # Merge the chunks if it doesn't exceed max_tokens
            if len(tokens) + len(next_tokens) <= max_tokens:
                chunk += " " + next_chunk
                tokens = tokenizer.encode(chunk)
        # Decode the chunk back into text
        chunk_text = tokenizer.decode(tokens, skip_special_tokens=True)
        # Add the chunk to the list if it's not empty or just "none"
        if chunk_text.strip() != "" and "none" not in chunk_text.lower():
            chunked_texts.append(chunk_text)
        # Move the starting point for the next chunk with overlap
        start = end - overlap_tokens  # Slide the window back by overlap size

    return chunked_texts


# Path to your PDF file
pdf_path = "/content/Cyber-Trust-V202208.cleaned.pdf"

# Extract text and tables from the PDF
pdf_text, table_text = extract_text_and_tables_from_pdf(pdf_path)

# Clean the extracted text
pdf_text = clean_text(pdf_text)
table_text = clean_text(table_text)  # Clean table text as well

# Chunk the pdf_text and table_text
pdf_text_chunks = chunk_text(pdf_text)
table_text_chunks = chunk_text(table_text)

# Now, pdf_text_chunks and table_text_chunks contain the chunked text data
print(f"Number of pdf_text chunks: {len(pdf_text_chunks)}")
print(f"Number of table_text chunks: {len(table_text_chunks)}")



import pandas as pd

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

# List of Excel files to process
excel_files = ["Capstone Dataset.xlsx", "Capstone Risk Data.xlsx"]  # Add all file paths

# Process all the files and get the structured data
structured_data = load_and_process_excel(excel_files)


def create_structured_text(sheet_name, row_data):
    # Combine sheet name, column headers, and values
    context = f"Sheet: {sheet_name}. "
    context += " | ".join([f"{key}: {value}" for key, value in row_data.items()])
    return context

# Generate context-rich strings
structured_texts = [create_structured_text(sheet_name, row) for sheet_name, row in structured_data]

print(structured_texts[301])


from astrapy import DataAPIClient
from sentence_transformers import SentenceTransformer
from sentence_transformers.cross_encoder import CrossEncoder

# Initialize your models
# bi_encoder = SentenceTransformer("sentence-transformers/multi-qa-mpnet-base-cos-v1")
bi_encoder = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")
cross_encoder = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")  # Use a cross-encoder model


# Initialize the client
client = DataAPIClient("AstraCS:fkZlYRRXBuIsirXCAkpdZPzh:391988e0eb5a8cad152e0b308cfb7bf9b6c6b918bf178ad82ab17d3ffa805385")
db = client.get_database_by_api_endpoint(
  "https://dd4da96d-4f77-4989-8109-5d70fa690131-us-east-2.apps.astra.datastax.com"
)

print(f"Connected to Astra DB: {db.list_collection_names()}")

collection = db.get_collection(
    "Capstone"
)

print(f"* Collection: {collection.full_name}\n")


# Combine the pdf_text_chunks and table_text_chunks into one list
all_chunks = pdf_text_chunks + table_text_chunks + structured_texts

# Encode all chunks
embeddings = bi_encoder.encode(all_chunks, normalize_embeddings=True)


# Prepare the documents in the required format
documents = [{"text": chunk, "$vector": embedding.tolist()} for chunk, embedding in zip(all_chunks, embeddings)]

insertion_result = collection.insert_many(documents)