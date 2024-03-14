from functools import wraps
from flask import (
    Blueprint,
    flash,
    redirect,
    request,
    session,
    abort,
    render_template,
    url_for,
)

# from routes.admin import authenticate
from db import db
from utils import (
    generate_passphrase,
    generate_pin,
    get_all_documents,
    get_current_timestamp,
    rangestr_to_list,
    get_documents_from_transactions,
)

from typing import Union

extension_blueprint = Blueprint("extension", __name__, url_prefix="/extension")


def requires_admin(f):
    @wraps(f)
    def decorated_route(*args, **kwargs):
        if session.get("admin"):
            return f(*args, **kwargs)

        flash("You need to be logged in!", "danger")
        return redirect(url_for("admin.login_page", after=request.full_path))

    return decorated_route


@extension_blueprint.get("/get_customer")
@requires_admin
def get_customer():
    username = request.args["username"]

    # get customer information
    customer: Union[dict, None] = db.customers.find_one(
        {"username": username}, {"_id": 0}
    )

    if customer is None:
        customer = {
            "username": username,
            "link": generate_passphrase(),
            "pin": generate_pin(),
            "remarks": "",
        }

    # then, get customers' transactions
    customer["transactions"] = list(
        db.transactions.find({"customer": username}, {"_id": 0})
    )
    customer["documents"] = get_documents_from_transactions(customer["transactions"])

    # TODO remove duplicates (although shouldnt happen)

    return render_template(
        "extension/chat.html", **customer, all_documents=get_all_documents()
    )


@extension_blueprint.post("/update_customer")
@requires_admin
def update():
    username = request.args["username"]

    if "amount" not in request.form or request.form["amount"] == "":
        flash("Missing amount")
        return redirect(url_for(".get_customer", username=username))
    try:
        float(request.form["amount"])
    except ValueError:
        flash("Invalid amount")
        return redirect(url_for(".get_customer", username=username))

    # get submitted documents
    documents = {}

    for key, _ in request.form.items():
        if key.startswith("doc-"):
            documents[key.replace("doc-", "", 1)] = []

    for key, value in request.form.items():
        if key.startswith("chapters-"):
            doc = key.replace("chapters-", "", 1)

            if not doc in documents:
                continue

            documents[doc] = rangestr_to_list(value)

    # get previous documents
    transactions = list(db.transactions.find({"customer": username}, {"_id": 0}))
    old_documents = get_documents_from_transactions(transactions)

    # diff to find out new documents (assume you cannot remove documents bc... how?)
    additions = {}
    for doc, chapters in documents.items():
        if not doc in old_documents:  # entirely new document added
            additions[doc] = chapters
            continue

        # maybe new chapters were added?
        for chapter in chapters:
            if chapter not in old_documents[doc]:
                if not doc in additions:
                    additions[doc] = []

                additions[doc].append(chapter)

    # splitting formula
    split = {
        "marcus": 0.6 if request.form["admin"] == "marcus" else 0.1,
        "ethan": 0.6 if request.form["admin"] == "ethan" else 0.1,
        "yc": 0.6 if request.form["admin"] == "yc" else 0.1,
        "jason": 0.6 if request.form["admin"] == "jason" else 0.1,
        "jx": 0.6 if request.form["admin"] == "jx" else 0.1,
    }

    db.customers.update_one(  # insert customer if first time
        {"username": username},
        {
            "$set": {
                "username": username,
                "link": request.form["link"].split("/")[-1],
                "pin": request.form["pin"],
                "remarks": "",
            }
        },
        upsert=True,
    )

    db.transactions.insert_one(
        {
            "customer": username,
            "timestamp": get_current_timestamp(),
            "amount": float(request.form["amount"]),
            "paid_out": False,
            "documents": additions,
            "admin": request.form["admin"],
            "split": split,
        }
    )

    flash("Updated")

    return redirect(url_for(".get_customer", username=username))
