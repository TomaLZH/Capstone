import hashlib
import pickle
import sqlalchemy
from Initialize import get_resources

# Get PostgreSQL engine
engine, _, _, _, _, _ = get_resources()

# Function to hash passwords using SHA-256


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Function to handle login and registration


def authenticate_user(username, password):
    with engine.connect() as conn:
        # Check if user exists
        result = conn.execute(sqlalchemy.text(
            "SELECT * FROM users WHERE username = :username"), {"username": username})
        user = result.fetchone()

        if user:  # User exists, attempt login
            # Assuming password is the 3rd column (index 2)
            stored_password = user[2]
            if stored_password == hash_password(password):
                return {"status": 200, "message": "Login successful!", "user": user}
            else:
                return {"status": 401, "message": "Invalid password!"}
        else:  # User not found, register them
            hashed_pw = hash_password(password)
            conn.execute(sqlalchemy.text("INSERT INTO users (username, password) VALUES (:username, :password)"),
                         {"username": username, "password": hashed_pw})
            conn.commit()

            # Fetch newly created user
            new_user_result = conn.execute(sqlalchemy.text("SELECT * FROM users WHERE username = :username"),
                                           {"username": username})
            new_user = new_user_result.fetchone()
            return {"status": 201, "message": "User registered successfully!", "user": new_user}

# Function to update user chat log


def update_chat_log(username, chat_data):
    with engine.connect() as conn:
        conn.execute(sqlalchemy.text("UPDATE users SET data = :data WHERE username = :username"),
                     {"data": pickle.dumps(chat_data), "username": username})
        conn.commit()

# Function to retrieve chat log


def get_chat_log(username):
    with engine.connect() as conn:
        result = conn.execute(sqlalchemy.text("SELECT data FROM users WHERE username = :username"),
                              {"username": username})
        chat_data = result.fetchone()

    if chat_data and chat_data[0]:
        return pickle.loads(chat_data[0])
    return None
