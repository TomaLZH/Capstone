import hashlib
import pickle
import sqlalchemy
from sqlalchemy.orm import sessionmaker
from Initialize import get_resources

# Get PostgreSQL engine
conn, _, _, _, _,_ = get_resources()

# Create session
Session = sessionmaker(bind=conn)
session = Session()

# Function to hash passwords using SHA-256
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Function to handle login and registration
def authenticate_user(username, password):
    with session as s:
        # Check if user exists
        result = s.execute(sqlalchemy.text("SELECT * FROM my_table WHERE username = :username"),
                           {"username": username})
        user = result.fetchone()

        if user:
            # Assuming password is the 3rd column (index 2)
            stored_password = user[2]
            if stored_password == hash_password(password):
                return {"status": 200, "message": "Login successful!", "user": user}
            else:
                return {"status": 401, "message": "Invalid password!"}
        else:
            # User not found, register them
            hashed_pw = hash_password(password)
            s.execute(sqlalchemy.text("INSERT INTO my_table (username, password) VALUES (:username, :password)"),
                      {"username": username, "password": hashed_pw})
            s.commit()

            # Fetch newly created user
            new_user_result = s.execute(sqlalchemy.text("SELECT * FROM my_table WHERE username = :username"),
                                        {"username": username})
            new_user = new_user_result.fetchone()
            return {"status": 201, "message": "User registered successfully!", "user": new_user}

# Function to update user chat log
def update_chat_log(username, chat_data):
    with session as s:
        s.execute(sqlalchemy.text("UPDATE my_table SET data = :data WHERE username = :username"),
                  {"data": pickle.dumps(chat_data), "username": username})
        s.commit()

# Function to retrieve chat log
def get_chat_log(username):
    with session as s:
        result = s.execute(sqlalchemy.text("SELECT data FROM my_table WHERE username = :username"),
                           {"username": username})
        chat_data = result.fetchone()

    if chat_data and chat_data[0]:
        return pickle.loads(chat_data[0])
    return None
