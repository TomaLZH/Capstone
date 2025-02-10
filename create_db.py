import streamlit as st
import pandas as pd

# Connect to PostgreSQL
conn = st.connection("postgresql", type="sql")

# Query to select all users
query = "SELECT * FROM users;"

# Execute query and fetch data into a Pandas DataFrame
df = conn.query(query)

# Display the data in Streamlit
print(df)
