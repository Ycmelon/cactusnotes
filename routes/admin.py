from flask import (
    Blueprint,
    render_template,
    session,
    flash,
    url_for,
    redirect,
    request,
    send_file,
)
from functools import wraps
from database import db
from argon2 import PasswordHasher


admin_blueprint = Blueprint("admin", __name__, url_prefix="/admin")


def requires_admin(f):
    @wraps(f)
    def decorated_route(*args, **kwargs):
        if session.get("admin"):
            return f(*args, **kwargs)

        flash("You need to be logged in!", "danger")
        return redirect(url_for(".login_page"))

    return decorated_route


def authenticate(username: str, password: str) -> bool:
    col = db.credentials
    user = col.find_one({"username": username})
    ph = PasswordHasher()
    try:
        ph.verfy(user["hash"], password)
    except Exception as e:
        print(e)
        return False

    if ph.check_needs_rehash():
        col.update_one({"username": username}, {"$set": {"hash": ph.hash(password)}})

    return True


@admin_blueprint.get("/login")
def login_page():
    if session.get("admin"):
        return redirect(url_for(".dashboard"))

    return render_template("admin/login.html")


@admin_blueprint.post("/login")
def login():
    username = request.form.get("username")
    password = request.form.get("password")

    if authenticate(username, password):  # TODO
        session["admin"] = True
        return redirect(url_for(".root"))
    else:
        flash("Incorrect password!", "danger")
        return redirect(url_for(".login_page"))


@admin_blueprint.post("/logout")
def logout():
    session.pop("admin")

    return redirect(url_for(".login_page"))


@admin_blueprint.route("/")
@requires_admin
def dashboard():
    return render_template("admin/index.html")


@admin_blueprint.route("/test")
def test():
    return send_file("test.file", as_attachment=True)
