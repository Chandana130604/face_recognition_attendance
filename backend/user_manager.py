from database.user_repository import UserRepository
from models.user import User
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
from pymongo.errors import DuplicateKeyError

class UserManager:
    def __init__(self):
        self.repo = UserRepository()

    def register_admin(self, username: str, password: str):
        if self.repo.find_by_username(username):
            raise ValueError("Username already exists")
        password_hash = generate_password_hash(password)
        user = User(
            username=username,
            password_hash=password_hash,
            role='admin',
            created_at=datetime.datetime.now()
        )
        try:
            return self.repo.insert(user)
        except DuplicateKeyError:
            raise ValueError("Username already exists")

    def authenticate(self, username: str, password: str) -> bool:
        user = self.repo.find_by_username(username)
        if user and check_password_hash(user.password_hash, password):
            return True
        return False
    
    # Add to existing UserManager class

def get_user_by_username(self, username):
    return self.repo.find_by_username(username)

def update_email(self, username, new_email):
    return self.repo.update_email(username, new_email)

def update_password(self, username, new_password):
    from werkzeug.security import generate_password_hash
    hashed = generate_password_hash(new_password)
    return self.repo.update_password(username, hashed)