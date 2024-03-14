from argon2 import PasswordHasher
from random import sample, choices
from datetime import datetime, timezone, timedelta

from db import db


def generate_passphrase():
    with open("wordlist.txt", "r") as f:
        wordlist = f.read().split("\n")
    return "-".join(sample(wordlist, 3))


def generate_pin() -> str:
    numbers = list(map(str, range(10)))
    return "".join(choices(numbers, k=6))


def salted_password_hash(password: str) -> str:
    """Generates a salted password hash using argon2-id"""
    ph = PasswordHasher()
    return ph.hash(password)


def create_user():
    from getpass import getpass

    db.credentials.insert_one(
        {
            "username": input("Username: "),
            "hash": salted_password_hash(getpass()),
            # "display_name": input("Name: "),
        }
    )


def rangestr_to_list(string):
    """ "1,4-7,10" -> [1,4,5,6,7,10]"""
    if string == "":
        return []

    result = []
    for part in string.split(","):
        if "-" in part:  # a range
            a, b = part.split("-")
            a, b = int(a), int(b)
            result.extend(range(a, b + 1))
        else:  # a number
            a = int(part)
            result.append(a)

    return result


def rangelist_to_str(list_):
    if len(list_) == 0:
        return ""

    result = []
    first = last = list_[0]
    for n in list_[1:]:
        if n - 1 == last:  # Part of the group, bump the end
            last = n
        else:  # Not part of the group, yield current group and start a new
            if first != last:
                result.append(f"{first}-{last}")
            else:
                result.append(str(first))

            first = last = n

    if first != last:
        result.append(f"{first}-{last}")
    else:
        result.append(str(first))

    return ", ".join(result)


def get_current_timestamp() -> int:
    return int(datetime.now().timestamp())  # utc timestamp (i think)


def get_datetime_str_from_timestamp(timestamp: int) -> str:
    return datetime.fromtimestamp(timestamp, timezone(timedelta(hours=8))).strftime(
        "%d/%m/%y %I:%M %p"
    )


def documents_to_items_str(documents: dict) -> str:
    """{'lowersec sci': [1,5,6] } -> 'lowersec sci (units 1-5, 6)"""
    output = []

    for doc, chapters in documents.items():
        if len(chapters) == 0:
            output.append(doc)
            continue

        output.append(f"{doc} (chapters {rangelist_to_str(chapters)})")

    return ", ".join(output)


def get_documents_from_transactions(transactions):
    output = {}  # file id: set(of chapters)

    for tsc in transactions:
        for document, chapters in tsc["documents"].items():
            if document in output:
                output[document].extend(chapters)
            else:
                output[document] = chapters

    return output


all_documents = list(db.documents.find({}, {"_id": 0}))  # trust it wont update


def get_all_documents():
    return all_documents  # trust


def get_filename_from_shortname(shortname: str) -> str:
    for doc in all_documents:
        if doc["shortname"] == shortname:
            return doc["filename"]

    raise KeyError


def get_document_info_from_shortname(shortname: str) -> dict:
    for doc in all_documents:
        if doc["shortname"] == shortname:
            return doc

    raise KeyError


def format_money(value: float) -> str:
    return f"${value:,.2f}".replace("$-", "-$")
