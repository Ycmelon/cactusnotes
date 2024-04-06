import os
from functools import wraps
from bson import ObjectId
from flask import (
    Blueprint,
    flash,
    redirect,
    request,
    session,
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
    get_timestamp_from_datetimelocal,
    rangestr_to_list,
    get_documents_from_transactions,
)

from typing import Union

extension_blueprint = Blueprint("extension", __name__, url_prefix="/extension")


DOMAIN = (
    "cactusnotes.co" if os.environ.get("MODE") == "production" else "localhost:5000"
)


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
    username = request.args.get("username", "").strip()

    # for action URLs to redirect back
    session["curr_url"] = url_for(
        ".get_customer",
        username=username,
        extension_mode=request.args.get("extension_mode"),
    )

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
    customer["transactions"] = [
        {**i, "_id": str(i["_id"])}  # convert objectids to str
        for i in db.transactions.find({"customer": username})
    ]
    customer["documents"] = get_documents_from_transactions(customer["transactions"])

    return render_template(
        "extension/chat.html",
        domain=DOMAIN,
        **customer,
        all_documents=get_all_documents(),
        extension_mode=True if request.args.get("extension_mode") else False
    )


@extension_blueprint.post("/update_customer")
@requires_admin
def update():
    username = request.args["username"].strip()

    # get submitted documents
    documents = {}

    for key, _ in request.form.items():
        if key.startswith("doc-"):
            # seems to only be "on" if checked otherwise it doesnt appear
            # as a key in the dict; thats why this works
            documents[key.replace("doc-", "", 1)] = []

    for key, value in request.form.items():
        if key.startswith("chapters-"):
            doc = key.replace("chapters-", "", 1)

            if not doc in documents:
                continue

            try:
                documents[doc] = rangestr_to_list(value)
            except:
                flash("Invalid range of chapters somewhere")
                return redirect(session["curr_url"])

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

    info = {
        "username": username,
        "link": request.form["link"].strip(),
        "pin": request.form["pin"].strip(),
        "remarks": "",
    }

    if "email" in request.form and request.form["email"]:
        info["email"] = request.form["email"]

    db.customers.update_one(  # insert customer if first time
        {"username": username},
        {"$set": info},
        upsert=True,
    )

    # only check amount here, so customer info i.e. email can be updated even
    # without transaction
    if "amount" not in request.form or request.form["amount"] == "":
        flash("No transaction was created as amount was not specified")
        return redirect(session["curr_url"])

    try:
        float(request.form["amount"])
    except ValueError:
        flash("Invalid amount")
        return redirect(session["curr_url"])

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

    return redirect(session["curr_url"])


@extension_blueprint.post("/update_transaction")
@requires_admin
def update_transaction():
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

            try:
                documents[doc] = rangestr_to_list(value)
            except:
                flash("Not updated: invalid range of chapters somewhere")
                return redirect(session["curr_url"])

    try:
        float(request.form["amount"])
    except ValueError:
        flash("Not updated: invalid amount")
        return redirect(session["curr_url"])

    db.transactions.update_one(
        {
            "_id": ObjectId(request.form["_id"]),
        },
        {
            "$set": {
                "timestamp": get_timestamp_from_datetimelocal(
                    request.form["timestamp"]
                ),
                "amount": float(request.form["amount"]),
                "admin": request.form["admin"],
                "documents": documents,
                # "paid_out": "paid_out" in request.form,
            }
        },
    )

    # print(request.form)
    flash("Transaction updated")
    return redirect(session["curr_url"])


@extension_blueprint.post("/delete_transaction")
@requires_admin
def delete_transaction():
    db.transactions.delete_one({"_id": ObjectId(request.form["_id"])})

    flash("Transaction successfully deleted")
    return redirect(session["curr_url"])
