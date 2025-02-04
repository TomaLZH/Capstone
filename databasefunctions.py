import sqlite3
import hashlib
import pickle

# Function to create a new database connection
def connect_db():
    return sqlite3.connect("sqlite3.db", check_same_thread=False)

# Function to hash passwords using SHA-256
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Function to handle login and registration
def authenticate_user(username, password):
    conn = connect_db()
    cursor = conn.cursor()

    # Check if user exists
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()

    if user:  # User exists, attempt login
        stored_password = user[2]  # Assuming password is the 3rd column (index 2)
        if stored_password == hash_password(password):
            conn.close()
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


# Function to update row with chat log
def update_chat_log(username, chat_data):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("UPDATE users SET data = ? WHERE username = ?", (chat_data, username))
    conn.commit()
    conn.close()

def get_chat_log(username):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT data FROM users WHERE username = ?", (username,))
    chat_data = cursor.fetchone()
    conn.close()
    if chat_data:
        return pickle.loads(chat_data[0])
    else:
        return None
