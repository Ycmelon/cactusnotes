from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import os

uri = f"mongodb+srv://kektwos:{os.environ.get('DATABASE_PW')}@cluster0.lctumyt.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(uri, server_api=ServerApi("1"))

try:
    client.admin.command("ping")
except Exception as e:
    print(e)

db = client.testing  # default to testing db for safety

if os.environ.get("MODE") == "production":
    db = client.sales
