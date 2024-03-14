from flask import (
    Blueprint,
    render_template,
    session,
    flash,
    url_for,
    redirect,
    request,
)
from functools import wraps
from db import db
from argon2 import PasswordHasher

from urllib.parse import quote_plus

from utils import get_current_timestamp, get_datetime_str_from_timestamp


admin_blueprint = Blueprint("admin", __name__, url_prefix="/admin")

ph = PasswordHasher()


def authenticate(username: str, password: str) -> bool:
    user = db.credentials.find_one({"username": username})
    if user is None:
        return False

    try:
        ph.verify(user.get("hash", ""), password)
    except Exception as e:
        print(e)
        return False

    if ph.check_needs_rehash(user["hash"]):
        db.credentials.update_one(
            {"username": username}, {"$set": {"hash": ph.hash(password)}}
        )

    return True


def requires_admin(f):
    @wraps(f)
    def decorated_route(*args, **kwargs):
        if session.get("admin"):
            return f(*args, **kwargs)

        flash("You need to be logged in!", "danger")
        return redirect(url_for(".login_page"))

    return decorated_route


@admin_blueprint.get("/login")
def login_page():
    if session.get("admin"):
        return redirect(url_for(".dashboard"))

    after = None  # redirect post-login? (for extension use)
    if request.args.get("after"):
        after = quote_plus(request.args["after"])

    return render_template("admin/login.html", after=after)


@admin_blueprint.post("/login")
def login():
    username = request.form.get("username")
    password = request.form.get("password")

    if username and password and authenticate(username, password):
        session["admin"] = username

        print(request.args, request.args.get("after"))
        if request.args.get("after"):  # redirect post-login? (for extension use)
            return redirect(request.args["after"])

        return redirect(url_for(".dashboard"))

    flash("Authentication error", "danger")
    return redirect(url_for(".login_page"))


@admin_blueprint.post("/logout")
def logout():
    session.pop("admin")

    return redirect(url_for(".login_page"))


@admin_blueprint.route("/")
@requires_admin
def dashboard():
    admins = ["marcus", "ethan", "yc", "jason", "jx"]

    transactions = db.transactions.find({}, {"amount": 1, "paid_out": 1, "split": 1})
    paid = {"total": 0, **{admin: 0 for admin in admins}}
    due = {"total": 0, **{admin: 0 for admin in admins}}
    total = {"total": 0, **{admin: 0 for admin in admins}}

    for tsc in transactions:
        total["total"] += tsc["amount"]
        for admin in admins:
            total[admin] += tsc["amount"] * tsc["split"][admin]

        if tsc["paid_out"]:
            paid["total"] += tsc["amount"]
            for admin in admins:
                paid[admin] += tsc["amount"] * tsc["split"][admin]
        else:
            due["total"] += tsc["amount"]
            for admin in admins:
                due[admin] += tsc["amount"] * tsc["split"][admin]

    return render_template(
        "admin/index.html", admins=admins, paid=paid, due=due, total=total
    )


@admin_blueprint.post("/payout")
@requires_admin
def payout():
    timestamp = get_current_timestamp()

    db.transactions.update_many(
        {"paid_out": False},
        {"$set": {"paid_out": True, "paid_out_timestamp": timestamp}},
    )

    flash(f"Paid out at {get_datetime_str_from_timestamp(timestamp)}", "success")

    return redirect(url_for(".dashboard"))


@admin_blueprint.get("/create_transaction")
@requires_admin
def create_transaction_form():
    return render_template("admin/create_transaction.html")


@admin_blueprint.post("/create_transaction")
@requires_admin
def create_transaction():
    timestamp = get_current_timestamp()

    if not request.form.get("customer") or not request.form.get("amount"):
        flash("Please fill all fields", "danger")
        return redirect(url_for(".create_transaction"))

    try:
        total_split = sum(
            [
                float(request.form["split-ethan"]),
                float(request.form["split-marcus"]),
                float(request.form["split-yc"]),
                float(request.form["split-jason"]),
                float(request.form["split-jx"]),
            ]
        )
        assert abs(total_split - 1) < 0.001 or abs(total_split) < 0.001
    except:
        flash(
            "There is an issue with the split (either invalid numbers entered or it doesn't add to 1 or 0)",
            "danger",
        )
        return redirect(url_for(".create_transaction"))

    db.transactions.insert_one(
        {
            "customer": request.form["customer"],
            "timestamp": timestamp,
            "amount": float(request.form["amount"]),
            "paid_out": False,
            "documents": {},
            "admin": session["admin"],
            "split": {
                "ethan": float(request.form["split-ethan"]),
                "marcus": float(request.form["split-marcus"]),
                "yc": float(request.form["split-yc"]),
                "jason": float(request.form["split-jason"]),
                "jx": float(request.form["split-jx"]),
            },
        }
    )

    flash("Created transaction", "primary")

    return redirect(url_for(".dashboard"))
