"""
Defines the `Certificate` model and adds functionality to easily store and retrieve certificate
information from the database.
"""
from __future__ import annotations
from bson import ObjectId
from bson.errors import InvalidId
from pymongo.results import InsertOneResult, UpdateResult
from app.models.user import User
from app.models.database import Database


class Certificate:
    """
    Represent a certificate. Provides functionality to easily store and retrieve certificate
    information from the database.
    """

    def __init__(
        self: Certificate, id_: str | None, name: str, title: str, certifier_id: str
    ) -> Certificate:
        """
        Initializes a new `Certificate` using the arguments provided. This method is mainly used
        internally to easily create instances in other methods. To create a new certificate in your
        code you may find easier using `Certificate.create` (usually followed by
        `Certificate.save`) instead.

        Args:
            id_: MongoDB provided object id.
            name: The name of the user to certify.
            title: The title of the certificate.
            certifier_id: The id of the certifier issuing this certificate.
        """
        self.id_ = id_
        self.name = name
        self.title = title
        self.certifier_id = certifier_id

    def get_certifier(self: Certificate) -> User | None:
        """
        Returns the certifier who issued this certificate. While usually it should not happen, this
        method can return None if no certifier with `self.certifier_id` was found. If this happens
        your data is likely to have errors.

        Returns:ID was not
            The certifier who issued this certificate. None if the certifier does not exist.
        """
        return User.get_by_id(self.certifier_id)

    def save(self: Certificate) -> InsertOneResult | UpdateResult:
        """
        Saves this certificate to the database. If this certificate had already been inserted before
        (determined by using its id_), this method updates it.

        Returns:
            The insert's `InsertOneResult` if the certificate was first inserted, or the update's
            `UpdateResult`if the certificate had already been inserted before and has been just
            updated.
        """
        # Get database
        db = Database.get()
        certificates = db["certificate-list"]

        # Update if it does not exist in database
        if self.id_:
            return certificates.update_one(
                {"_id": ObjectId(self.id_)},
                {
                    "$set": {
                        "name": self.name,
                        "title": self.title,
                        "certifier_id": self.certifier_id,
                    }
                },
            )
        # If it has been just created, insert
        else:
            insert_result = certificates.insert_one(
                {
                    "name": self.name,
                    "title": self.title,
                    "certifier_id": self.certifier_id,
                }
            )
            self.id_ = str(insert_result.inserted_id)
            return insert_result

    @staticmethod
    def create(name: str, title: str, certifier_id: str) -> Certificate:
        """
        Creates a new `Certificate` using the arguments provided. This method does not save the
        certificate to the database (for that call the `Certificate.save` method in the
        `Certificate` instead).

        Args:
            name: The name of the user to certify.
            title: The title of the certificate.
            certifier_id: The id of the certifier issuing this certificate.
        Returns:
            The newly created user (without id).
        """
        return Certificate(None, name, title, certifier_id)

    @staticmethod
    def get_by_id(id_: str) -> Certificate:
        """
        Retrieves the certificate with the given id from the database and returns it.

        Args:
            id_: The id of the object to search.
        Returns:
            The certificate with the given id, if one was found. None otherwise.
        """
        # Check that id format is valid
        try:
            object_id = ObjectId(id_)
        except InvalidId:
            return None
        # Get database and retrieve object
        db = Database.get()
        certificate = db["certificate-list"].find_one({"_id": object_id})
        # Return result
        if not certificate:
            return None
        return Certificate(
            str(certificate["_id"]),
            certificate["name"],
            certificate["title"],
            certificate["certifier_id"],
        )
