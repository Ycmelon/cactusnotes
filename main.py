from flask import Flask
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
    get_filename_from_shortname,
    rangelist_to_str,
)

from rclone import rclone_pull


app = Flask(__name__)
# cors = CORS(
#     app,
#     resources={r"/api/*": {"origins": "https://www.carousell.sg"}},
#     supports_credentials=True,
# )

app.secret_key = "hehe"
app.template_folder = "./routes/templates"

# custom filters
app.jinja_env.filters["rangelist_to_str"] = rangelist_to_str
app.jinja_env.filters["documents_to_items_str"] = documents_to_items_str
app.jinja_env.filters["get_datetime_str_from_timestamp"] = (
    get_datetime_str_from_timestamp
)
app.jinja_env.filters["get_filename_from_shortname"] = get_filename_from_shortname
app.jinja_env.filters["format_money"] = format_money


app.register_blueprint(admin_blueprint)
app.register_blueprint(extension_blueprint)
app.register_blueprint(customer_blueprint)


@app.get("/script")
def get_script():  # tampermonkey script
    with open("./extension/script.js", "r") as file:
        script = file.read()

    with open("./extension/sidebar.html", "r") as file:
        script.replace("{{ sidebar }}", file.read())

    return script


rclone_pull()

if __name__ == "__main__":
    app.run("0.0.0.0")
