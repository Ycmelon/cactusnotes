import os
from flask import (
    Blueprint,
    request,
    send_file,
    session,
    abort,
    render_template,
    flash,
    redirect,
    url_for,
    send_from_directory,
)

from db import db
from pdf import pdf_from_pages
from utils import (
    get_current_timestamp,
    get_document_info_from_shortname,
    rangelist_to_str,
    get_documents_from_transactions,
)


customer_blueprint = Blueprint(
    "customer_blueprint",
    __name__,
)


@customer_blueprint.get("/<code>")
def access_customer(code: str):
    customer = db.customers.find_one({"link": code.strip()})

    if customer is None:  # this code is invalid
        abort(404)

    if session.get("customer") != customer["username"]:  # not signed in
        return render_template("customer/login.html")

    # signed in, present with documents
    transactions = db.transactions.find({"customer": customer["username"]})
    documents = get_documents_from_transactions(transactions)

    return render_template(
        "customer/dashboard.html",
        **customer,
        documents=documents,
    )


@customer_blueprint.post("/<code>")
def customer_login(code: str):
    pin = request.form.get("pin", "").strip()

    customer = db.customers.find_one({"link": code.strip()})
    if customer is None:
        abort(404)

    if customer["pin"] != pin:  # if pin wrong
        flash("Incorrect password!", "danger")
        return redirect(url_for(".access_customer", code=code))

    # otherwise
    db.analytics.insert_one(
        {
            "customer": customer["username"],
            "type": "login",
            "timestamp": get_current_timestamp(),
            "user_agent": request.headers.get("User-Agent"),
            "ip_address": request.remote_addr,
        }
    )

    session["customer"] = customer["username"]  # set logged in
    return redirect(url_for(".access_customer", code=code))


@customer_blueprint.get("/download/studyguide/<shortname>")
def download_studyguide(shortname: str):
    if session.get("customer") is None:  # not signed in
        abort(401)

    transactions = db.transactions.find({"customer": session["customer"]})
    documents = get_documents_from_transactions(
        transactions
    )  # gets all documents, so potentially inefficient

    if shortname not in documents:
        abort(403)

    filename = get_document_info_from_shortname(shortname)["studyguide"]

    db.analytics.insert_one(
        {
            "customer": session["customer"],
            "type": "download",
            "document": f"{shortname} studyguide",
            "timestamp": get_current_timestamp(),
            "user_agent": request.headers.get("User-Agent"),
            "ip_address": request.remote_addr,
        }
    )

    return send_from_directory("./drive", filename, as_attachment=True)


@customer_blueprint.get("/download/<shortname>")
def download_document(shortname: str):
    if session.get("customer") is None:  # not signed in
        abort(401)

    transactions = db.transactions.find({"customer": session["customer"]})
    documents = get_documents_from_transactions(
        transactions
    )  # gets all documents, so potentially inefficient

    if shortname not in documents:
        abort(403)

    filename = get_document_info_from_shortname(shortname)["filename"]

    db.analytics.insert_one(
        {
            "customer": session["customer"],
            "type": "download",
            "document": shortname,
            "timestamp": get_current_timestamp(),
            "user_agent": request.headers.get("User-Agent"),
            "ip_address": request.remote_addr,
        }
    )

    if len(documents[shortname]) == 0:  # full file
        return send_from_directory("./drive", filename, as_attachment=True)

    else:  # only certain chapters
        document_info = get_document_info_from_shortname(shortname)

        pages = set()
        pages.update(document_info["chapter_pages"].get("default", []))
        for chapter in documents[shortname]:
            pages.update(document_info["chapter_pages"][str(chapter)])

        sliced_filename = pdf_from_pages(
            os.path.join("./drive", filename),
            pages,
            f"(chapters {rangelist_to_str(documents[shortname])})",
        )
        return send_file(sliced_filename, as_attachment=True)


@customer_blueprint.post("/logout")
def customer_logout():
    session.pop("customer")
    return "Logged out"  # TODO


@customer_blueprint.errorhandler(404)
def not_found(error):
    return (
        render_template(
            "customer/message.html",
            content="Link not found, please check for typos!",
            title="Not found",
        ),
        404,
    )


@customer_blueprint.errorhandler(401)
@customer_blueprint.errorhandler(403)
def auth_errors(error):
    return (
        render_template(
            "customer/message.html",
            content=f"Please login again via the link provided to you! ({error})",
            title="Authentication error",
        ),
        404,
    )


@customer_blueprint.errorhandler(500)
def unknown_error(error):
    return (
        render_template(
            "customer/message.html",
            content=f"An unknown error occured, please contact us! ({error})",
            title="Unknown error",
        ),
        500,
    )
