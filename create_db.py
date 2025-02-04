import sqlite3

# Connect to SQLite database
conn = sqlite3.connect('sqlite3.db')

# Create a cursor object
cursor = conn.cursor()

# Create a table
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    data BLOB
)
''')

# Commit the changes and close the connection
conn.commit()
conn.close()