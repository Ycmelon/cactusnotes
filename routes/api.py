from functools import wraps
from flask import Blueprint, request, session, abort

from routes.admin import authenticate
from database import db
from utils import shortname_from_id


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
def check():
    username = request.form.get("username")
    col = db.transactions
    results = list(
        col.find({"customer.username": username}, {"paid": 0, "splitting": 0})
    )

    data = {
        "url": None,
        "pin": None,
        "authorised": {},
        "transactions": [],
        "legend": {},
    }
    if len(results) == 0:
        return data

    for r in results:  # each r is a transaction
        # from each transaction: require date + money +
        # what is bought (doc_id, shortname and chapters)
        t2 = []
        for item in r["sold"]:
            _id = str(item["doc_id"])
            chapters = item["chapters"]
            if _id not in data["legend"]:
                data["legend"][_id] = shortname_from_id(_id)
            if _id not in data["authorised"]:
                data["authorised"][_id] = []
            data["authorised"][_id].extend(chapters)

            t2.append(
                {
                    "id": _id,
                    "chapters": chapters,
                }
            )

        t = {
            "date": r["date"].timestamp(),
            "money": r["money"],
            "bought": t2,
        }
        data["transactions"].append(t)
    data["url"] = results[0]["customer"]["url"]
    data["pin"] = results[0]["customer"]["pin"]
    return data

@api_blueprint.post("/update")
@requires_admin
def update(username: str):
    pass
