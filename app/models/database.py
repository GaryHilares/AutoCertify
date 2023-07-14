from os import environ
from flask import g
from pymongo import MongoClient


class Database:
    @staticmethod
    def get_client():
        client = getattr(g, "db_client", None)
        if not client:
            username = environ["DB_USERNAME"]
            password = environ["DB_PASSWORD"]
            hostname = environ["DB_HOSTNAME"]
            connection_string = f"mongodb+srv://{username}:{password}@{hostname}/?retryWrites=true&w=majority"
            g.db_client = client = MongoClient(connection_string)
        return client

    @staticmethod
    def get():
        """
        Connects to the Mongo database specified by the environment variables.

        Returns:
            database (MongoDatabase)
                A database connection to the database specified by the
                environment variables.
        """
        client = Database.get_client()
        db = client["project2"]
        return db
