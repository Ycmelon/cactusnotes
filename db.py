from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import os
import certifi

from dotenv import load_dotenv

load_dotenv()

uri = os.environ.get("MONGODB_URI")
if not uri:
    raise KeyError("No MongoDB URI specified")

client = MongoClient(
    uri,
    server_api=ServerApi("1"),
    tlsCAFile=certifi.where(),
    connect=False,
    maxPoolSize=1,
)

# try:
#     client.admin.command("ping")
# except Exception as e:
#     print(e)

db = client.testing  # default to testing db

if os.environ.get("MODE") == "production":
    db = client.sales
