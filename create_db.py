import streamlit as st
import pandas as pd
import base64
import pickle

# Connect to PostgreSQL
conn = st.connection("postgresql", type="sql")

# Fetch data, encoding BYTEA in base64
df = conn.query("SELECT ID, Username, Password, encode(data, 'base64') AS data FROM my_table")

# Function to decode base64 and unpickle
def decode_and_unpickle(data):
    if data:
        try:
            binary_data = base64.b64decode(data)  # Decode base64
            return pickle.loads(binary_data)  # Unpickle
        except Exception as e:
            return f"Error unpickling: {str(e)}"
    return None

# Apply decoding to the 'Data' column
df["data"] = df["data"].apply(decode_and_unpickle)

# Print the decoded skill levels (or error message) in the terminal
for data in df["data"]:
    if hasattr(data, "get_skill_level"):
        print(data.get_skill_level())  # Print skill level to terminal
    else:
        print("No skill level method found in the decoded object.")  # Print error message if no method

# Print the full DataFrame to terminal
print(df)
