"""
Includes a `MockUtils` class that mocks the `Utils` class
"""


class MockUtils:
    """
    Mocks the `Utils` namespace-like class.
    """

    @staticmethod
    def check_metadata(url: str, name: str, content: str) -> bool:
        """
        Mocks `check_metadata` function. Assumes there is only one website, whose domain is example.com
        and has the `ca-key` metadata tag set to `ca-key-example`.
        """
        return (
            url == "example.com" and name == "ca-key" and content == "ca-key-someuser"
        )
