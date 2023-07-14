"""
FILE
    utils.py
DESCRIPTION
    Provides utilities for the "Certificate Automation" Flask app. This
    includes comparing dictionaries for deep structural equality, connecting
    to the database, managing requests to websites, and more.
"""
from os import environ
from bs4 import BeautifulSoup
from pymongo import MongoClient
import requests


def get_database() -> any:
    """
    Connects to the Mongo database specified by the environment variables.

    Returns:
        database (MongoDatabase)
            A database connection to the database specified by the
            environment variables.
    """
    # Retrieve authentication data from environment
    username = environ["DB_USERNAME"]
    password = environ["DB_PASSWORD"]
    hostname = environ["DB_HOSTNAME"]

    # Connect to the MongoDB cluster
    connection_string = (
        f"mongodb+srv://{username}:{password}@{hostname}/?retryWrites=true&w=majority"
    )
    client = MongoClient(connection_string)

    # Return "project2" database
    return client["project2"]


def check_metadata(url: str, name: str, content: str) -> bool:
    """
    Checks whether a website has a `meta` tag set to an specific value.

    Arguments:
        url (str)
            Website's url.
        name (str)
            Name of the `meta` tag to search.
        content (str)
            Expected value of the `meta` tag
    Returns:
        True if the website at `url` has a `meta` tag with `name="{name}"`
        and `content="{content}"`. False otherwise..
    """
    # Retrieve URL
    response = requests.get(url, timeout=3)  # error if url is invalid
    meta_elements = BeautifulSoup(response.text).find_all("meta")

    # Iterate over meta elements
    return any(
        element.attrs.get("name", None) == name
        and element.attrs.get("content", None) == content
        for element in meta_elements
    )


def same_structure(dict1: any, dict2: any) -> bool:
    """
    Checks whether two dictionaries have the same structure recursively. It is considered
    that two objects are of the same structure if they are two non-dictionary objects of
    the same type or if they are two dictionaries whose keys are equal and values have
    the same structure.

    Arguments:
        dict1 (any)
            The first variable to compare.
        dict2 (any)
            The second variable to compare.
    Returns:
        True if dict2's structure matches dict1's, False otherwise.
    """
    # Base case: At least one of dict1 or dict2 is not a dict, so just compare types.
    if not isinstance(dict1, dict) or not isinstance(dict2, dict):
        return type(dict1) is type(dict2)

    # Recursive case: Both dict1 or dict2 are dict, so check elements recursively
    return not any(
        key not in dict2 or not same_structure(dict1[key], dict2[key]) for key in dict1
    )