import streamlit as st
import sqlalchemy

# Connect to PostgreSQL
conn = st.connection("postgresql", type="sql")

# # Insert data safely using session.execute()
# with conn.session as session:
#     session.execute(
#         sqlalchemy.text("INSERT INTO my_table (username, password) VALUES (:username, :password)"),
#         {"username": "John", "password": "12345"}  # Use parameterized queries
#     )
#     session.commit()  # Commit the transaction

# Fetch and display data
df = conn.query("SELECT * FROM my_table")

st.write("Users in database:")
for _, row in df.iterrows():
    print(f"Username: {row['username']}, Password: {row['password']}")
    
# Alter the table to change the password column type
# with conn.session as session:
#     session.execute(
#         sqlalchemy.text("ALTER TABLE my_table ALTER COLUMN password TYPE VARCHAR(255)")
#     )
#     session.commit()  # Commit the transaction