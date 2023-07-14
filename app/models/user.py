"""
FILE
    user.py
DESCRIPTION
    Defines the user model.
"""

from flask_login import UserMixin


class User(UserMixin):
    """
    Represent an user. Provides functionality
    required for log in.
    """

    def __init__(self, user_id):
        super().__init__()
        self.id = user_id
