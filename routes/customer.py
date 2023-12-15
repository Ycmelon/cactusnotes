from flask import (
    Blueprint,
    request,
    session,
    abort,
    render_template,
    flash,
    redirect,
    url_for,
)

from database import db
from utils import shortname_from_id


customer_blueprint = Blueprint("customer_blueprint", __name__, url_prefix="/access")


@customer_blueprint.get("/<code>")
def access_customer(code: str):
    print("here!", code)
    transactions = list(db.get_collection("transactions").find({"customer.url": code}))

    if len(transactions) == 0:  # this code is invalid
        abort(404)

    if session.get("customer") != code:  # not signed in
        return render_template("access/login.html")

    # signed in, present with documents
    customer = transactions[0]["customer"]
    return render_template("access/dashboard.html", username=customer["username"])


@customer_blueprint.post("/<code>")
def customer_login(code: str):
    pin = request.form.get("pin")

    transaction = db.get_collection("transactions").find_one({"customer.url": code})
    if transaction == None:
        abort(404)

    if transaction["customer"]["pin"] != pin:  # if pin wrong
        flash("Incorrect password!", "danger")
        return redirect(url_for(".access_customer", code=code))

    # otherwise
    session["customer"] = code  # set logged in
    return redirect(url_for(".access_customer", code=code))


@customer_blueprint.route("/logout")  # for testing
def customer_logout():
    session.pop("customer")
    return "done"
