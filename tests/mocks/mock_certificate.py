"""
Includes a `MockCertificate` class that mocks the `Certificate` class
"""
from __future__ import annotations
from types import SimpleNamespace
from tests.mocks.mock_user import MockUser


class MockCertificate:
    """
    Mocks the `Certificate` class.
    """

    def __init__(
        self, id_: str, name: str, title: str, certifier_id: str | None
    ) -> MockCertificate:
        """
        Data to use for the mock.

        Args:
            id_; Mocks a MongoDB's id.
            name: Mocks receiver's name.
            title: Mocks receiver's title
            certifier_id: Mocks certifier's id
        """
        super().__init__()
        self.id_ = id_
        self.name = name
        self.title = title
        self.certifier_id = certifier_id

    def get_certifier(self: MockCertificate) -> MockUser:
        ret = MockUser.get_by_id(self.certifier_id)
        print(ret)
        return ret

    def save(self: MockCertificate) -> None:
        """
        Mocks the `save` function. Returns mock inserted_id.
        """
        return SimpleNamespace(inserted_id="somecertificate")

    @staticmethod
    def get_by_id(id_: str) -> MockCertificate:
        """
        Mocks the `get_by_id` function, retrieving certificates from the "if-else database".
        """
        if id_ == "anid":
            return MockCertificate(None, "goodperson", "goodtitle", "someid")
        return None

    @staticmethod
    def create(title: str, name: str, certifier_id: str) -> MockCertificate:
        """
        Mocks the `create` function, creating a new `MockCertificate` and returning it.

        Args:
            name: The mock receiver's name.
            title: The mock receiver's title.
        Returns:
            The newly created mock certificate (without id).
        """
        return MockCertificate(None, title, name, certifier_id)
