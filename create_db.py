import sqlite3

# Connect to SQLite database
conn = sqlite3.connect('sqlite3.db')
cursor = conn.cursor()

# Drop the existing table (if it exists)
cursor.execute('DROP TABLE IF EXISTS users')

# Recreate the table with the new columns
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    username TEXT NOT NULL,
    password TEXT NOT NULL,
    data BLOB
)
''')

# Commit the changes and close the connection
conn.commit()
conn.close()