import hashlib
import pickle
import sqlalchemy
from sqlalchemy.orm import sessionmaker
from Chat import Chat
from Initialize import get_resources

# Get PostgreSQL engine
conn, _, _, _, _, _ = get_resources()

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
        result = s.execute(sqlalchemy.text("SELECT * FROM users WHERE username = :username"),
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
            s.execute(sqlalchemy.text("INSERT INTO users (username, password) VALUES (:username, :password)"),
                      {"username": username, "password": hashed_pw})
            s.commit()

            # Fetch newly created user
            new_user_result = s.execute(sqlalchemy.text("SELECT * FROM users WHERE username = :username"),
                                        {"username": username})
            new_user = new_user_result.fetchone()
            return {"status": 201, "message": "User registered successfully!", "user": new_user}


def update_company_infrastructure(username, infrastructure):
    with session as s:
        s.execute(sqlalchemy.text("UPDATE users SET infrastructure = :infrastructure WHERE username = :username"),
                  {"infrastructure": infrastructure, "username": username})
        s.commit()

def update_skilllevel(username, skill_level):
    with session as s:
        s.execute(sqlalchemy.text("UPDATE users SET skill_level = :skill_level WHERE username = :username"),
                  {"skill_level": skill_level, "username": username})
        s.commit()

def update_checklist(username, check_list):
    with session as s:
        s.execute(sqlalchemy.text("UPDATE users SET check_list = :check_list WHERE username = :username"),
                  {"check_list": check_list, "username": username})
        s.commit()



#Evaluation table functions

def add_evaluation(question, my_answer):
    with session as s:
        s.execute(sqlalchemy.text("INSERT INTO Evaluation (question, my_answer) VALUES (:question, :my_answer)"),
                  {"question": question, "my_answer": my_answer})
        s.commit()

def add_gpt_answer(question, gpt_answer):
    try:
        with session as s:
            s.execute(sqlalchemy.text("UPDATE Evaluation SET gpt_answer = :gpt_answer WHERE question = :question"),
                      {"gpt_answer": gpt_answer, "question": question})
            s.commit()
        print("Updated gpt_answer successfully.")
    except Exception as e:
        print(f"Error updating gpt_answer: {e}")
