# pylint: disable=duplicate-code
import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

client = MongoClient(MONGO_URI)

db = client["dinnermeet"]  # database name

# Collections
users_collection = db["users"]
events_collection = db["events"]
