import os
import secrets
from flask import Flask, redirect
from flask_cors import CORS

from dotenv import load_dotenv


load_dotenv()

from routes.admin import admin_blueprint
from routes.extension import extension_blueprint
from routes.customer import customer_blueprint

from utils import (
    documents_to_items_str,
    format_money,
    get_datetime_str_from_timestamp,
    get_datetimelocal_from_timestamp,
    get_filename_from_shortname,
    rangelist_to_str,
)

from rclone import rclone_pull


app = Flask(__name__)

app.secret_key = os.environ["SECRET_KEY"]
app.template_folder = "./routes/templates"

# for chrome-based browsers
app.config.update(SESSION_COOKIE_SAMESITE="None", SESSION_COOKIE_SECURE=True)

# custom filters
app.jinja_env.filters["rangelist_to_str"] = rangelist_to_str
app.jinja_env.filters["documents_to_items_str"] = documents_to_items_str
app.jinja_env.filters["get_datetime_str_from_timestamp"] = (
    get_datetime_str_from_timestamp
)
app.jinja_env.filters["get_filename_from_shortname"] = get_filename_from_shortname
app.jinja_env.filters["format_money"] = format_money
app.jinja_env.filters["get_datetimelocal_from_timestamp"] = (
    get_datetimelocal_from_timestamp
)


app.register_blueprint(admin_blueprint)
app.register_blueprint(extension_blueprint)
app.register_blueprint(customer_blueprint)


@app.get("/script")
def get_script():  # tampermonkey script
    domain = "http://localhost:5000"
    if os.environ.get("MODE") == "production":
        domain = "https://cactusnotes.co"

    with open("./extension/script.js", "r") as file:
        script = file.read().replace("{{ domain }}", domain)

    return script


@app.get("/samples")
def get_samples():
    return redirect("https://linktr.ee/cactusnotes")


@app.get("/")
def index():  # no home page yet so samples i guess
    return redirect("https://linktr.ee/cactusnotes")


rclone_pull()

if __name__ == "__main__":
    app.run(debug=True)
