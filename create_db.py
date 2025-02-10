import streamlit as st
from sqlalchemy import text  # Import text() from SQLAlchemy

# Connect to PostgreSQL
conn = st.connection("postgresql", type="sql")

# SQL Query to create the table
create_table_query =    text("""
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    infrastructure TEXT,
    checklist JSONB,
    skill_level TEXT
);
"""
)
# Execute the query
# Use session.execute() for DDL queries
with conn.session as session:
    session.execute(create_table_query)
    session.commit()  # Commit changes

st.success("Table 'users' created successfully with a JSONB checklist!")
