from random import sample, choices
from argon2 import PasswordHasher
from database import db
from cachetools import cached, TTLCache
from bson import ObjectId


@cached(cache=TTLCache(maxsize=10, ttl=60))
def shortname_from_id(id):
    return db.documents.find_one({"_id": ObjectId(id)})["shortname"]


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
