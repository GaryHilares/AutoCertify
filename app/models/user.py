"""
FILE
    user.py
DESCRIPTION
    Defines the user model.
"""
from bson import ObjectId
from flask_login import UserMixin
from app.models.database import Database


class User(UserMixin):
    """
    Represent an user. Provides functionality
    required for log in.
    """

    def __init__(self, id_: ObjectId | None, name: str, password: any, url: str):
        super().__init__()
        self.id_ = id_
        self.name = name
        self.password = password
        self.url = url

    def get_id(self):
        return self.id_

    def set_verified(self, url):
        self.url = url

    def save(self) -> None:
        db = Database.get()
        users = db["certifiers"]
        if self.id_:
            return users.update_one(
                {"_id": self.id_},
                {
                    "$set": {
                        "name": self.name,
                        "password": self.password,
                        "url": self.url,
                    }
                },
            )
        else:
            return users.insert_one({self.name, self.password, self.url})

    @staticmethod
    def create(name, password):
        return User(None, name, password, "None")

    @staticmethod
    def get_by_id(id_):
        db = Database.get()
        certifier = db["certifiers"].find_one({"_id": id_})
        if not certifier:
            return None
        return User(
            certifier["_id"], certifier["name"], certifier["password"], certifier["url"]
        )

    @staticmethod
    def get_by_name(user_name):
        db = Database.get()
        certifier = db["certifiers"].find_one({"name": user_name})
        if not certifier:
            return None
        return User(
            certifier["_id"], certifier["name"], certifier["password"], certifier["url"]
        )
