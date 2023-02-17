from pymongo import MongoClient
import requests
from bs4 import BeautifulSoup
from os import environ

def get_database():
    # Connect to the MongoDB cluster
    CONNECTION_STRING = f'mongodb+srv://{environ["DB_USERNAME"]}:{environ["DB_PASSWORD"]}@{environ["DB_HOSTNAME"]}/?retryWrites=true&w=majority'
    client = MongoClient(CONNECTION_STRING)

    # Return "project2" database
    return client["project2"]

def check_metadata(url, name, content):
    # Retrieve URL
    response = requests.get(url) # error if url is invalid
    meta_elements = BeautifulSoup(response.text).find_all('meta')

    # Iterate over meta elements
    for element in meta_elements:
        # Check if the metadata information matches
        if element.attrs.get('name', None) == name and element.attrs.get('content', None) == content:
            return True
    
    # Metadata information did not match, so return false
    return False