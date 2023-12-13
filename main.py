from flask import Flask, render_template

from routes.admin import admin_blueprint
from routes.api import api_blueprint
from database import db

app = Flask(__name__)

app.secret_key = "hehe"
app.template_folder = "./routes/templates"

app.register_blueprint(admin_blueprint)
app.register_blueprint(api_blueprint)

if __name__ == "__main__":
    app.run("0.0.0.0")
