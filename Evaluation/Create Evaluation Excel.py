import pandas as pd
import streamlit as st
from sqlalchemy import text

# Connect to PostgreSQL
conn = st.connection("postgresql", type="sql")

# Retrieve rows from database to put into new Excel file
query = """
SELECT * FROM Evaluation;
"""

# Execute the query using conn and wrap the query in `text()`
with conn.session as session:
    result = session.execute(text(query)).fetchall()

# Create Excel file

df = pd.DataFrame(result, columns=["id", "question", "my_answer", "my_grade", "gpt_answer", "gpt_grade",
                  "reason", "better_answer", "advanced_answer", "advanced_gpt_grade", "better_advanced_answer"])
df.to_excel("evaluation.xlsx", index=False)
