from pymongo import MongoClient
from app.config import MONGODB_URI, DB_NAME, COLLECTION_NAME

def init_mongo_client():
    """
    Initialize and return a MongoDB client connected to the specified database and collection.
    
    Returns:
        Collection: The MongoDB collection object.
    """
    client = MongoClient(MONGODB_URI())
    return client[DB_NAME()][COLLECTION_NAME()]

def fetch_document(collection, key):
    """
    Fetch a document from the MongoDB collection based on the provided key.
    
    Args:
        collection (Collection): The MongoDB collection object.
        key (str): The key to search for in the 'words' field.
    
    Returns:
        dict: The document found, or None if no document matches the key.
    """
    return collection.find_one({"words": key})
