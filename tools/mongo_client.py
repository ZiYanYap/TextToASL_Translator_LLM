import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DB_NAME = os.getenv("DB_NAME", "asl_project")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "word_metadata")

def init_mongo_client():
    uri = os.getenv("MONGODB_URI")
    client = MongoClient(uri)
    return client[DB_NAME][COLLECTION_NAME]
