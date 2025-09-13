import os
from typing import Any, Dict

from pymongo import MongoClient
from pymongo.database import Database
from pymongo.errors import CollectionInvalid

from app.core.config import settings

# --- Database and Collection Names ---
DB_NAME = "sentiment_analysis_db"
ENTITIES_COLLECTION = "entities"
ANALYSIS_RESULTS_COLLECTION = "analysis_results"
SOURCES_YOUTUBE_COLLECTION = "sources_youtube"
COMMENTS_YOUTUBE_COLLECTION = "comments_youtube"


def get_db_client() -> MongoClient:
    """
    Creates and returns a MongoDB client using the connection string from settings.
    """
    client: MongoClient = MongoClient(settings.MONGODB_CONNECTION_STRING)
    return client


def create_collection_with_validator(
    db: Database, collection_name: str, validator: Dict[str, Any]
) -> None:
    """
    Creates a collection with a specified JSON schema validator.
    If the collection already exists, it attempts to modify it to apply the validator.
    """
    try:
        db.create_collection(collection_name)
        print(f"Collection '{collection_name}' created.")
    except CollectionInvalid:
        print(f"Collection '{collection_name}' already exist. Skipping creation.")

    db.command("collMod", collection_name, validator=validator)
    print(f"Validator applied to '{collection_name}'.")


def setup_database() -> None:
    """
    Main function to set up the database and all collections with their schemas.
    """
    client: MongoClient | None = None
    try:
        client = get_db_client()
        # Check connection
        client.admin.command("ping")
        print("Successfully connected to MongoDB Atlas!")

        db: Database = client[DB_NAME]

        # --- Schema Validators ---

        entities_validator: Dict[str, Any] = {
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["keyword", "geo", "volume", "start_date"],
                "properties": {
                    "keyword": {"bsonType": "string"},
                    "geo": {"bsonType": "string"},
                    "volume": {"bsonType": "int"},
                    "start_date": {"bsonType": "date"},
                },
            }
        }

        analysis_results_validator: Dict[str, Any] = {
            "$jsonSchema": {
                "bsonType": "object",
                "required": [
                    "entity_id",
                    "analysis_type",
                    "created_at",
                    "status",
                    "results",
                ],
                "properties": {
                    "entity_id": {"bsonType": "objectId"},
                    "analysis_type": {"enum": ["weekly", "on_demand"]},
                    "created_at": {"bsonType": "date"},
                    "status": {
                        "enum": ["pending", "processing", "completed", "failed"]
                    },
                    "results": {
                        "bsonType": "object",
                        "properties": {
                            "positive_count": {"bsonType": "int"},
                            "negative_count": {"bsonType": "int"},
                            "neutral_count": {"bsonType": "int"},
                            "total_comments": {"bsonType": "int"},
                            "source_video_count": {"bsonType": "int"},
                        },
                    },
                },
            }
        }

        sources_youtube_validator: Dict[str, Any] = {
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["entity_id", "video_id", "url", "title", "publish_date"],
                "properties": {
                    "entity_id": {"bsonType": "objectId"},
                    "video_id": {"bsonType": "string"},
                    "url": {"bsonType": "string"},
                    "title": {"bsonType": "string"},
                    "publish_date": {"bsonType": "date"},
                },
            }
        }

        comments_youtube_validator: Dict[str, Any] = {
            "$jsonSchema": {
                "bsonType": "object",
                "required": [
                    "source_id",
                    "comment_id",
                    "text",
                    "author",
                    "publish_date",
                ],
                "properties": {
                    "source_id": {"bsonType": "objectId"},
                    "comment_id": {"bsonType": "string"},
                    "text": {"bsonType": "string"},
                    "author": {"bsonType": "string"},
                    "publish_date": {"bsonType": "date"},
                },
            }
        }

        # --- Create Collections ---
        print("\nStarting database setup...")
        create_collection_with_validator(db, ENTITIES_COLLECTION, entities_validator)
        create_collection_with_validator(
            db, ANALYSIS_RESULTS_COLLECTION, analysis_results_validator
        )
        create_collection_with_validator(
            db, SOURCES_YOUTUBE_COLLECTION, sources_youtube_validator
        )
        create_collection_with_validator(
            db, COMMENTS_YOUTUBE_COLLECTION, comments_youtube_validator
        )
        print("\nDatabase setup completed successfully!")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if client:
            client.close()
            print("MongoDB connection closed.")


if __name__ == "__main__":
    setup_database()
