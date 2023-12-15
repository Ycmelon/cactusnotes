from flask import Flask
from flask_cors import CORS

from dotenv import load_dotenv

load_dotenv()

from routes.admin import admin_blueprint
from routes.api import api_blueprint
from routes.customer import customer_blueprint

from rclone import rclone_pull


app = Flask(__name__)
cors = CORS(
    app,
    resources={r"/api/*": {"origins": "https://www.carousell.sg"}},
    supports_credentials=True,
)

app.secret_key = "hehe"
app.template_folder = "./routes/templates"

app.register_blueprint(admin_blueprint)
app.register_blueprint(api_blueprint)
app.register_blueprint(customer_blueprint)

if __name__ == "__main__":
    rclone_pull()
    app.run("0.0.0.0")
