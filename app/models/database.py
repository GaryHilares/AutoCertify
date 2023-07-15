"""
Module containing the namespace-like class `Database`, which includes utilities for working with the
database.
"""
from os import environ
from flask import g
from pymongo import MongoClient
from pymongo.database import Database as MongoDatabase


class Database:
    """
    Namespace-like class that implements database utilities, including getting the database client
    and main database for this application.
    """

    @staticmethod
    def get_client() -> MongoClient:
        """
        Lazily opens a connection to MongoDB, stores it in the application context for future use,
        and returns it.

        Returns:
            A MongoClient connection to the cluster specified by the environment variables.
        """
        client = getattr(g, "db_client", None)
        if not client:
            username = environ["DB_USERNAME"]
            password = environ["DB_PASSWORD"]
            hostname = environ["DB_HOSTNAME"]
            connection_string = (
                f"mongodb+srv://{username}:{password}@{hostname}/?w=majority"
            )
            g.db_client = client = MongoClient(connection_string)
        return client

    @staticmethod
    def get() -> MongoDatabase:
        """
        Retrieves the default MongoDB database for this application (called `project2`) and returns
        it. This method calls `Database.get_client`, opening a connection to the cluster if one does
        not already exist.

        Returns:
            The default MongoDB database for this application.
        """
        client = Database.get_client()
        db = client["project2"]
        return db
