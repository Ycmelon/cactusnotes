from functools import wraps
from flask import Blueprint, request, session, abort

from routes.admin import authenticate
from database import db


api_blueprint = Blueprint("api", __name__, url_prefix="/api")


def requires_admin(f):
    @wraps(f)
    def decorated_route(*args, **kwargs):
        if session.get("admin"):
            return f(*args, **kwargs)
        abort(401)

    return decorated_route


@api_blueprint.post("/login")
def login():
    username = request.form.get("username")
    password = request.form.get("password")

    if authenticate(username, password):
        session["admin"] = True


@api_blueprint.post("/check")
@requires_admin
def check(username: str):
    col = db.transactions
    results = list(
        col.find({"customer.username": username}, {"paid": 0, "splitting": 0})
    )
    return results


@api_blueprint.post("/update")
@requires_admin
def update(username: str):
    pass
