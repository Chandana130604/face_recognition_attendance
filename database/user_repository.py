from database.mongodb_connection import Database
from models.user import User
from datetime import datetime
from typing import Optional

class UserRepository:
    def __init__(self):
        self.collection = Database().get_collection("users")
        self.collection.create_index("username", unique=True)

    def insert(self, user: User) -> str:
        user_dict = {
            "username": user.username,
            "password_hash": user.password_hash,
            "role": user.role,
            "employee_id": user.employee_id,
            "failed_attempts": user.failed_attempts,
            "locked_until": user.locked_until,
            "last_login": user.last_login,
            "created_at": user.created_at or datetime.now()
        }
        result = self.collection.insert_one(user_dict)
        return str(result.inserted_id)

    def find_by_username(self, username: str) -> Optional[User]:
        doc = self.collection.find_one({"username": username})
        if doc:
            return User(
                _id=str(doc["_id"]),
                username=doc["username"],
                password_hash=doc["password_hash"],
                role=doc["role"],
                employee_id=doc.get("employee_id"),
                failed_attempts=doc.get("failed_attempts", 0),
                locked_until=doc.get("locked_until"),
                last_login=doc.get("last_login"),
                created_at=doc.get("created_at")
            )
        return None

    def update_failed_attempts(self, username: str, attempts: int, locked_until=None):
        update = {"$set": {"failed_attempts": attempts}}
        if locked_until:
            update["$set"]["locked_until"] = locked_until
        self.collection.update_one({"username": username}, update)

    def reset_failed_attempts(self, username: str):
        self.collection.update_one(
            {"username": username},
            {"$set": {"failed_attempts": 0, "locked_until": None}}
        )

    def update_last_login(self, username: str):
        self.collection.update_one(
            {"username": username},
            {"$set": {"last_login": datetime.now()}}
        )

    def change_password(self, username: str, new_password_hash: str):
        result = self.collection.update_one(
            {"username": username},
            {"$set": {"password_hash": new_password_hash}}
        )
        return result.modified_count > 0