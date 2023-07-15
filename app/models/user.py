"""
Defines the `User` model and adds functionality to easily store and retrieve user information from
the database.
"""
from __future__ import annotations
from bson import ObjectId
from bson.errors import InvalidId
from pymongo.results import InsertOneResult, UpdateResult
from flask_login import UserMixin
from app.models.database import Database


class User(UserMixin):
    """
    Represent an user. Provides functionality to easily store and retrieve user information from the
    database.
    """

    def __init__(
        self, id_: str | None, name: str, password: str, url: str | None
    ) -> User:
        """
        Initializes a new `User` using the arguments provided. This method is mainly used internally
        to easily create instances in other methods. To create a new user in your code you may find
        easier using `User.create` (usually followed by `User.save`) instead.

        Args:
            id_: MongoDB provided object id.
            name: The name of the user to create.
            password: The password hash of the user to create.
            url: The verified URL of the user, if one exists.
        """
        super().__init__()
        self.id_ = id_
        self.name = name
        self.password = password
        self.url = url

    def get_id(self: User) -> ObjectId | None:
        """
        Returns the user id. Internally used by `flask_login` to manage user log in.

        Returns:
            The MongoDB provided user id, if this user has one. None otherwise.
        """
        return self.id_

    def set_verified(self: User, url: str) -> None:
        """
        Sets this user as verified, adding the `url` argument as its verified URL.

        Args:
            url: This user's new verified URL.
        """
        self.url = url

    def save(self: User) -> InsertOneResult | UpdateResult:
        """
        Saves this user to the database. If this user had already been inserted before (determined
        by using its id_), this method updates it.

        Returns:
            The insert's `InsertOneResult` if the user was first inserted, or the update's
            `UpdateResult`if the user had already been inserted before and has been just updated.
        """
        # Get database
        db = Database.get()
        users = db["certifiers"]

        # Update if it does not exist in database
        if self.id_:
            return users.update_one(
                {"_id": ObjectId(self.id_)},
                {
                    "$set": {
                        "name": self.name,
                        "password": self.password,
                        "url": self.url,
                    }
                },
            )
        # If it has been just created, insert
        else:
            insert_result = users.insert_one(
                {"name": self.name, "password": self.password, "url": self.url}
            )
            self.id_ = str(insert_result.inserted_id)
            return insert_result

    @staticmethod
    def create(name: str, password: str) -> User:
        """
        Creates a new `User` using the arguments provided. This method does not save the user to the
        database (for that call the `User.save` method in the `User` instead).

        Args:
            name: The name of the user to create.
            password: The password hash of the user to create.
        Returns:
            The newly created user (without id nor verified URL).
        """
        return User(None, name, password, None)

    @staticmethod
    def get_by_id(id_: str) -> User:
        """
        Retrieves the user with the given id from the database and returns it.

        Args:
            id_: The id of the object to search.
        Returns:
            The user with the given id, if one was found. None otherwise.
        """
        try:
            object_id = ObjectId(id_)
        except InvalidId:
            return None
        db = Database.get()
        certifier = db["certifiers"].find_one({"_id": object_id})
        if not certifier:
            return None
        return User(
            str(certifier["_id"]),
            certifier["name"],
            certifier["password"],
            certifier["url"],
        )

    @staticmethod
    def get_by_name(name: str) -> User:
        """
        Retrieves a user with the given name from the database and returns it.

        Args:
            name: The name of the object to search.
        Returns:
            The user with the given name, if one was found. None otherwise.
        """
        db = Database.get()
        certifier = db["certifiers"].find_one({"name": name})
        if not certifier:
            return None
        return User(
            str(certifier["_id"]),
            certifier["name"],
            certifier["password"],
            certifier["url"],
        )
