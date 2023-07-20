"""
Provides utilities for the "Certificate Automation" Flask app. This includes comparing dictionaries
for deep structural equality, connecting to the database, managing requests to websites, and more.
"""
from bs4 import BeautifulSoup
import requests


class Utils:
    """
    Namespace-like class wrapper for utils functions. Note that this "namespace" is necessary for
    `pytest-mock`s to work as intended (by referring to this module rather than the module where
    utils are imported from).
    """

    @staticmethod
    def check_metadata(url: str, name: str, content: str) -> bool:
        """
        Checks whether a website has a `meta` tag set to an specific value.

        Arguments:
            url: Website's url.
            name: Name of the `meta` tag to search.
            content: Expected value of the `meta` tag
        Returns:
            True if the website at `url` has a `meta` tag with `name="{name}"` and
            `content="{content}"`. False otherwise.
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

    @staticmethod
    def same_structure(dict1: any, dict2: any) -> bool:
        """
        Checks whether two dictionaries have the same structure recursively. It is considered that two
        objects are of the same structure if they are two non-dictionary objects of the same type or if
        they are two dictionaries whose keys are equal and values have the same structure.

        Arguments:
            dict1: The first variable to compare.
            dict2: The second variable to compare.
        Returns:
            True if dict2's structure matches dict1's, False otherwise.
        """
        # Base case: At least one of dict1 or dict2 is not a dict, so just compare types.
        if not isinstance(dict1, dict) or not isinstance(dict2, dict):
            return type(dict1) is type(dict2)

        # Recursive case: Both dict1 or dict2 are dict, so check elements recursively
        return len(dict1) == len(dict2) and not any(
            key not in dict2 or not Utils.same_structure(dict1[key], dict2[key])
            for key in dict1
        )
