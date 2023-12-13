from flask import Blueprint, render_template, session, flash, url_for, redirect, request
from functools import wraps


admin_blueprint = Blueprint("admin", __name__, url_prefix="/admin")


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

    return render_template("admin/login.html")


@admin_blueprint.post("/login")
def login():
    username = request.form.get("username")
    password = request.form.get("password")

    # magic auth here
    # if request.form.get("password") == ADMIN_PASSWORD:  # TODO
    #     session["admin"] = True
    #     return redirect(url_for(".root"))
    # else:
    #     flash("Incorrect password!", "danger")
    #     return redirect(url_for(".login_page"))


@admin_blueprint.post("/logout")
def logout():
    session.pop("admin")

    return redirect(url_for(".login_page"))


@admin_blueprint.route("/")
@requires_admin
def dashboard():
    return render_template("admin/index.html")
