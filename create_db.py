import streamlit as st
import pandas as pd
import base64
import pickle

# Import the Chat class from chat.py
from Chat import Chat

# Clear any existing cache
st.cache_data.clear()
st.cache_resource.clear()

# Connect to PostgreSQL
conn = st.connection("postgresql", type="sql")

# Fetch data from the database
df = conn.query("SELECT * FROM my_table")
print(df)