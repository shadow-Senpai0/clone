# database.py
"""
Database operations for the Auto Forward Bot
"""

from pymongo import MongoClient
import logging
from config import MONGODB_URI, DATABASE_NAME, CHANNELS_COLLECTION, USERS_COLLECTION

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize MongoDB Client
mongo_client = MongoClient(MONGODB_URI)
db = mongo_client[DATABASE_NAME]
channels_collection = db[CHANNELS_COLLECTION]
users_collection = db[USERS_COLLECTION]

def initialize_channels():
    """
    Initialize or update the channels configuration in MongoDB.
    Returns the default or existing configuration.
    """
    default_config = {"_id": "config", "sources": [], "target": None, "selected_source": None}
    existing_config = channels_collection.find_one({"_id": "config"})
    if not existing_config:
        channels_collection.insert_one(default_config)
        logger.info("Initialized default channels configuration in MongoDB")
        return default_config
    if "sources" not in existing_config or "target" not in existing_config or "selected_source" not in existing_config:
        channels_collection.update_one(
            {"_id": "config"},
            {"$set": {"sources": existing_config.get("sources", []), "target": existing_config.get("target", None), "selected_source": existing_config.get("selected_source", None)}},
            upsert=True
        )
        logger.info("Updated existing channels configuration with missing keys")
        return channels_collection.find_one({"_id": "config"})
    return existing_config

def save_channels(channels):
    """
    Save the channels configuration to MongoDB.
    """
    channels_collection.update_one({"_id": "config"}, {"$set": channels}, upsert=True)

def load_users():
    """
    Load all user IDs from the users collection.
    """
    return [doc["user_id"] for doc in users_collection.find()]
