"""
Includes a `MockUser` class that mocks the `User` class
"""
from __future__ import annotations
from flask_login import UserMixin


class MockUser(UserMixin):
    """
    Mocks the `User` class.
    """

    def __init__(self, id_: str, name: str, password: str, url: str | None) -> MockUser:
        """
        Data to use for the mock.

        Args:
            id_; Mocks a MongoDB's id.
            name: Mocks user's name.
            password: Mocks user's password hash.
            url: Mock user's verified URL.
        """
        super().__init__()
        self.id_ = id_
        self.name = name
        self.password = password
        self.url = url

    def get_id(self: MockUser) -> str:
        """
        Mocks the `get_id` function required by `flask-login` to handle login.

        Returns:
            The mocked MongoDB's id.
        """
        return self.id_

    def save(self: MockUser) -> None:
        """
        Mocks the `save` function. No-op.
        """
        pass

    @staticmethod
    def get_by_name(name: str) -> MockUser | None:
        """
        Mocks the `get_by_name` function, retrieving users from the mock "if-else database".

        Returns:
            The mocked MongoDB's id.
        """
        if name == "someuser":
            # User's password is 1234
            return MockUser(
                "someid",
                "someuser",
                b"$2b$12$St2gvjcv1nzl.ZaDqHIhLO1gLNsoZ1MB7gmO8yrHigI0j7rXx6pUW",
                None,
            )
        return None

    @staticmethod
    def create(name: str, password: str) -> MockUser:
        """
        Mocks the `create` function, creating a new `MockUser` and returning it.

        Args:
            name: The name of the user to create.
            password: The password hash of the user to create.
        Returns:
            The newly created mock user (without id nor verified URL).
        """
        return MockUser(None, name, password, None)
