from random import sample, choices
from argon2 import PasswordHasher
from database import db
from cachetools import cached, TTLCache
from bson import ObjectId


@cached(cache=TTLCache(maxsize=10, ttl=60))
def shortname_from_id(id):
    return db.documents.find_one({"_id": ObjectId(id)})["name"]


def generate_passphase():
    with open("wordlist.txt", "r") as f:
        wordlist = f.read().split("\n")
    return "-".join(sample(wordlist, 3))


def generate_pin():
    numbers = list(map(str, range(10)))
    return "".join(choices(numbers, k=6))


def salted_password_hash(password: str) -> str:
    """Generates a salted password hash using argon2-id"""
    ph = PasswordHasher()
    return ph.hash(password)


def create_user():
    from getpass import getpass

    col = db.credentials.insert_one(
        {
            "username": input("Username: "),
            "hash": salted_password_hash(getpass()),
            "display_name": input("Name: "),
        }
    )


def check(username: str):
    col = db.transactions
    results = list(
        col.find({"customer.username": username}, {"paid": 0, "splitting": 0})
    )

    data = {"url": None, "pin": None, "authorised": [], "transactions": []}
    if len(results) == 0:
        return data

    for r in results:  # each r is a transaction
        # from each transaction: require date + money +
        # what is bought (doc_id, shortname and chapters)
        data["transactions"].append(
            {
                "date": r["date"],
                "money": r["money"],
                "bought": [
                    {
                        "id": item["doc_id"],
                        "shortname": shortname_from_id(item["doc_id"]),
                        "chapters": item["chapters"],
                    }
                    for item in r["sold"]
                ],
            }
        )
    return data


print(check("jeff bozos"))
