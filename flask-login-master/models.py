from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, id, username, email, password):
        self.id = id
        self.username = username
        self.email = email
        self.password = password

# In-memory "database" for simplicity
users = {}
user_counter = 1

def create_user(username, email, password):
    global user_counter
    user = User(user_counter, username, email, password)
    users[user_counter] = user
    user_counter += 1
    return user

def get_user_by_email(email):
    for user in users.values():
        if user.email == email:
            return user
    return None
