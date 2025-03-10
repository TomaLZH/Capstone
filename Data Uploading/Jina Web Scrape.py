from pymilvus import MilvusClient
import requests
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer


url = 'https://r.jina.ai/https://www.csa.gov.sg/our-programmes/support-for-enterprises/sg-cyber-safe-programme/cybersecurity-certification-for-organisations/cyber-trust/certification-for-the-cyber-trust-mark/'
headers = {
    'Authorization': 'Bearer jina_76808bd9e69146e7ba02d21b0615c3eaXOhFQIHyWoUiK3mnAe4uhCQRRSIZ'
}

# tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
tokenizer = AutoTokenizer.from_pretrained(
    "sentence-transformers/all-mpnet-base-v2")


response = requests.get(url, headers=headers)


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


# Chunk Text
text = response.text
text_chunks = chunk_text(text)

# Embed it

# bi_encoder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
model = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")

# Encode all chunks
embeddings = model.encode(text_chunks, normalize_embeddings=True)


# Upload to Milvus


client = MilvusClient(uri="https://in03-6d0166da8e21ddd.serverless.gcp-us-west1.cloud.zilliz.com",
                      token="")

client.describe_collection(collection_name="Capstone")

# # Prepare the documents in the required format
documents = [{"text": chunk, "vector": embedding.tolist()}
             for chunk, embedding in zip(text_chunks, embeddings)]


res = client.insert(
    collection_name="Capstone",
    data=documents,
    ids=None,
    wait=True
)
