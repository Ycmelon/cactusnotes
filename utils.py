from random import sample, choices
from argon2 import PasswordHasher
from typing import Tuple


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


hash1 = salted_password_hash("abc123")
print(hash1)
