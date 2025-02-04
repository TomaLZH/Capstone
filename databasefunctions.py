import sqlite3
import hashlib

# Function to create a new database connection
def connect_db():
    return sqlite3.connect("sqlite3.db", check_same_thread=False)

# Function to hash passwords using SHA-256
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Function to handle login/register in one function
def authenticate_user(username, password):
    conn = connect_db()  # Create a new connection for this function
    cursor = conn.cursor()

    # Check if the user exists
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()

    if user:  # User exists, attempt login
        if user[2] == hash_password(password):  # Assuming `password` is at index 2
            conn.close()  # Close connection after use
            return {"status": 200, "message": "Login successful!", "user": user}
        else:
            conn.close()
            return {"status": 401, "message": "Invalid password!"}

    else:  # User not found, register them
        hashed_pw = hash_password(password)
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_pw))
        conn.commit()

        # Fetch newly created user
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        new_user = cursor.fetchone()
        conn.close()
        return {"status": 201, "message": "User registered successfully!", "user": new_user}
