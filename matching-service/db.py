import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

client = MongoClient(MONGO_URI)

db = client["dinnermeet"]  # database name

# Collections, doesn't need chat
users_collection = db["users"]
events_collection = db["events"]
