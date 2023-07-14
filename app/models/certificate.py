from bson import ObjectId
from app.models.user import User
from app.models.database import Database


class Certificate:
    def __init__(
        self, id_: ObjectId | None, name: str, title: str, certifier_id: ObjectId
    ):
        self.id_ = id_
        self.name = name
        self.title = title
        self.certifier_id = certifier_id

    def get_certifier(self):
        return User.get_by_id(self.certifier_id)

    @staticmethod
    def create(name: str, title: str, certifier_id: ObjectId):
        return Certificate(None, name, title, certifier_id)

    @staticmethod
    def get_by_id(id_):
        db = Database.get()
        certificate = db["certificate-list"].find_one({"_id": id_})
        if not certificate:
            return None
        return Certificate(
            certificate["_id"],
            certificate["name"],
            certificate["title"],
            certificate["certifier_id"],
        )

    def save(self):
        db = Database.get()
        users = db["certifiers"]
        if self.id_:
            return users.update_one(
                {"_id": self.id_},
                {
                    "$set": {
                        "name": self.name,
                        "title": self.title,
                        "certifier_id": self.certifier_id,
                    }
                },
            )
        else:
            return users.insert_one({self.name, self.title, self.certifier_id})
