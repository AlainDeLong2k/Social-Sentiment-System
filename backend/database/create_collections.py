import os
from dotenv import load_dotenv, find_dotenv
from pymongo import MongoClient
import json
from datetime import datetime as dt, timedelta
import pprint

load_dotenv(find_dotenv())

MONGODB_URI = os.getenv("MONGODB_URI")

printer = pprint.PrettyPrinter()

client = MongoClient(MONGODB_URI)
dbs = client.list_database_names()
trending_db = client.trending_db


def create_entities_collection():
    entities_validator = {
        "$jsonSchema": {
            "bsonType": "object",
            "required": [
                "keyword",
                "geo",
                "volume",
                "volume_growth_pct",
                "start_date",
                "trend_keywords",
            ],
            "properties": {
                "keyword": {
                    "bsonType": "string",
                    "description": "must be a string and is required",
                },
                "geo": {
                    "bsonType": "string",
                    "description": "must be a string and is required",
                },
                "volume": {
                    "bsonType": "int",
                    "minimum": 0,
                    "description": "must be an integer greater than 0 and is required",
                },
                "volume_growth_pct": {
                    "bsonType": "int",
                    "minimum": 0,
                    "description": "must be an integer greater than 0 and is required",
                },
                "start_date": {
                    "bsonType": "date",
                    "description": "must be a date and is required",
                },
                "trend_keywords": {
                    "bsonType": "array",
                    "items": {
                        "bsonType": "string",
                        "description": "must be a string and is required",
                    },
                },
            },
        }
    }

    try:
        trending_db.create_collection("entities")
    except Exception as e:
        print(e)

    trending_db.command("collMod", "entities", validator=entities_validator)


def create_youtube_videos_collection():
    videos_validator = {
        "$jsonSchema": {
            "bsonType": "object",
            "required": [
                "id",
                "url",
                "title",
                "publish_date",
                "description",
                "thumbnail",
                "entity_id",
            ],
            "properties": {
                "id": {
                    "bsonType": "string",
                    "description": "must be a string and is required",
                },
                "url": {
                    "bsonType": "string",
                    "description": "must be a string and is required",
                },
                "title": {
                    "bsonType": "string",
                    "description": "must be a string and is required",
                },
                "publish_date": {
                    "bsonType": "date",
                    "description": "must be a date and is required",
                },
                "description": {
                    "bsonType": "string",
                    "description": "must be a string and is required",
                },
                "thumbnail": {
                    "bsonType": "string",
                    "description": "must be a string and is required",
                },
                "entity_id": {
                    "bsonType": "objectId",
                    "description": "must be an objectId and is required",
                },
            },
        }
    }

    try:
        trending_db.create_collection("youtube_videos")
    except Exception as e:
        print(e)

    trending_db.command("collMod", "youtube_videos", validator=videos_validator)


def create_youtube_comments_collection():
    comments_validator = {
        "$jsonSchema": {
            "bsonType": "object",
            "required": [
                "entity_id",
                "video_id",
                "author",
                "text",
                # "like_count",
                "publish_date",
                "sentiment",
            ],
            "properties": {
                "entity_id": {
                    "bsonType": "objectId",
                    "description": "must be an objectId and is required",
                },
                "video_id": {
                    "bsonType": "string",
                    "description": "must be an string and is required",
                },
                "author": {
                    "bsonType": "string",
                    "description": "must be a string and is required",
                },
                "text": {
                    "bsonType": "string",
                    "description": "must be a string and is required",
                },
                # "like_count": {
                #     "bsonType": "int",
                #     "minimum": 0,
                #     "description": "must be an integer greater than or equal 0 and is required",
                # },
                "publish_date": {
                    "bsonType": "date",
                    "description": "must be a date and is required",
                },
                "sentiment": {
                    "enum": ["positive", "neutral", "negative"],
                    "description": "can only be one of the enum values and is required",
                },
            },
        }
    }

    try:
        trending_db.create_collection("youtube_comments")
    except Exception as e:
        print(e)

    trending_db.command("collMod", "youtube_comments", validator=comments_validator)


def main():
    # print(MONGODB_URI)
    print(dbs)

    create_entities_collection()
    create_youtube_videos_collection()
    create_youtube_comments_collection()


if __name__ == "__main__":
    main()
