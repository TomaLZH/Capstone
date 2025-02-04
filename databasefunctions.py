import sqlite3
import hashlib
from Initialize import get_resources

conn, cursor, bi_encoder, cross_encoder, collection, openai_client, assistant = get_resources()

# Function to hash passwords using SHA-256


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Function to handle login/register in one function


def authenticate_user(username, password):
    # Check if the user exists
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()

    if user:  # User exists, attempt login
        # Assuming `password` is at index 2
        if user[2] == hash_password(password):
            # Return full user data
            return {"status": 200, "message": "Login successful!", "user": user}
        else:
            # Unauthorized
            return {"status": 401, "message": "Invalid password!"}

    else:  # User not found, register them
        hashed_pw = hash_password(password)
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_pw))
        conn.commit()

        # Fetch newly created user
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        new_user = cursor.fetchone()

        # Created
        return {"status": 201, "message": "User not found. Registered successfully!", "user": new_user}
