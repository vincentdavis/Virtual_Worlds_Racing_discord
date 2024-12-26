"""DB utilities."""

import os

from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()


# def initialize_mongo():
#     """Initialize and connect to MongoDB using environment variables."""
#     mongo_uri = os.environ.get("MONGO_URI", "mongodb://localhost:27017")
#     database_name = os.environ.get("MONGO_DB", "default_db")
#     client = MongoClient(mongo_uri)
#     return client[database_name]
#
#
# db = initialize_mongo()
# collections = db.list_collection_names()
# print(collections)
# db.create_collection("club_admins")
# print(collections)
# "67663f62b4deb5b6ba3fff27"
