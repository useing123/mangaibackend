from datetime import datetime
from typing import Optional

from bson.objectid import ObjectId
from pymongo.database import Database
from pymongo.errors import DuplicateKeyError

from ..utils.security import hash_password


class AuthRepository:
    def __init__(self, database: Database):
        self.database = database
        self.database["users"].create_index("email", unique=True)  

    def create_user(self, user: dict):
        payload = {
            "email": user["email"],
            "password": hash_password(user["password"]),
            "created_at": datetime.utcnow(),
        }

        try:
            self.database["users"].insert_one(payload)
        except DuplicateKeyError:
            raise  # Повторно выбрасываем исключение

    def get_user_by_id(self, user_id: str) -> Optional[dict]:
        user = self.database["users"].find_one(
            {
                "_id": ObjectId(user_id),
            }
        )
        return user

    def get_user_by_email(self, email: str) -> Optional[dict]:
        user = self.database["users"].find_one(
            {
                "email": email,
            }
        )
        return user

    def update_user(self, user_id: str, update_data: dict):
        self.database["users"].update_one(
            {"_id": ObjectId(user_id)},
            {"$set": update_data},
        )

    def count_users(self) -> int:
        return self.database["users"].count_documents({})
