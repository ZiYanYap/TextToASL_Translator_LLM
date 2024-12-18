from pymongo import MongoClient
from app.config import MONGODB_URI, DB_NAME, COLLECTION_NAME

def init_mongo_client():
    client = MongoClient(MONGODB_URI())
    return client[DB_NAME()][COLLECTION_NAME()]
