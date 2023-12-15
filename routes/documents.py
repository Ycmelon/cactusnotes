from functools import wraps
from flask import Blueprint, request, session, abort

from routes.admin import authenticate
from database import db


documents_blueprint = Blueprint("documents", __name__, url_prefix="/documents")


def requires_login(f):
    @wraps(f)
    def decorated_route(*args, **kwargs):
        # if session.get("admin"):
        #     return f(*args, **kwargs)
        # abort(401)
        return f(*args, **kwargs)

    return decorated_route


@documents_blueprint.route("/")
@requires_login
def get_document():
    shortname = request.args.get("shortname")  # TODO

    # TODO check whether this user has bought
    # TODO get only the chapters the user has bought
