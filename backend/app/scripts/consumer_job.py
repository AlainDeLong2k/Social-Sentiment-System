from typing import Any, List, Dict
import json
import time
from datetime import datetime
from confluent_kafka import Consumer, KafkaError, Message

from pymongo import MongoClient
from pymongo.database import Database
from bson.objectid import ObjectId

from app.core.config import settings
from app.services.sentiment_service import SentimentService


def process_message_batch(
    batch: List[Message],
    sentiment_service: SentimentService,
    db: Database,
) -> None:
    """
    Processes a batch of Kafka messages: performs sentiment analysis and updates all database collections.
    """
    if not batch:
        return

    print(f"Processing a batch of {len(batch)} messages...")

    # --- 1. Prepare data for the model ---
    messages_data: List[Dict[str, Any]] = []
    texts_to_predict: List[str] = []

    for msg in batch:
        message_data = json.loads(msg.value().decode("utf-8"))
        messages_data.append(message_data)
        texts_to_predict.append(
            message_data.get("video_and_comment_data", {}).get("text", "")
        )

    if not texts_to_predict:
        print("Batch contains only empty comments after preprocessing. Skipping.")
        return

    # --- 2. Perform Batch Sentiment Analysis ---
    predictions = sentiment_service.predict_batch(texts_to_predict)

    # --- 3. Save data to Database ---
    video_id_cache: Dict[str, ObjectId] = {}
    comments_to_insert: List[Dict[str, Any]] = []

    for message_data, prediction in zip(messages_data, predictions):
        entity_keyword = message_data.get("entity_keyword")
        entity_thumbnail = message_data.get("entity_thumbnail_url")
        entity_volume = message_data.get("entity_volume")
        data = message_data.get("video_and_comment_data", {})

        video_id = data.get("video_id")
        video_title = data.get("video_title")
        video_publish_date_str = data.get("video_publish_date")
        video_url = data.get("video_url")

        sentiment_label = prediction["label"].lower()

        if not all([entity_keyword, entity_volume is not None, video_id]):
            continue

        # 3a. Upsert Entity and get its ID
        entity_doc = db.entities.find_one_and_update(
            {"keyword": entity_keyword},
            {
                "$setOnInsert": {
                    "keyword": entity_keyword,
                    "geo": settings.FETCH_TRENDS_GEO,
                    "volume": entity_volume,
                    "thumbnail_url": entity_thumbnail,
                    "start_date": datetime.now(),
                }
            },
            upsert=True,
            return_document=True,
        )
        entity_id = entity_doc["_id"]

        # 3b. Upsert Source Video and get its ID (with in-batch caching)
        source_id: ObjectId | None = video_id_cache.get(video_id)
        if not source_id:
            source_doc = db.sources_youtube.find_one_and_update(
                {"video_id": video_id},
                {
                    "$setOnInsert": {
                        "entity_id": entity_id,
                        "video_id": video_id,
                        "url": video_url,
                        "title": video_title,
                        "publish_date": datetime.strptime(
                            video_publish_date_str, "%Y-%m-%dT%H:%M:%SZ"
                        ),
                    }
                },
                upsert=True,
                return_document=True,
            )
            source_id = source_doc["_id"]
            video_id_cache[video_id] = source_id

        # 3c. Prepare comment for bulk insertion
        comments_to_insert.append(
            {
                "source_id": source_id,
                "comment_id": data.get("comment_id"),
                "text": data.get("text"),
                "author": data.get("author"),
                "publish_date": datetime.strptime(
                    data.get("publish_date"), "%Y-%m-%dT%H:%M:%SZ"
                ),
            }
        )

        # 3d. Update Aggregated Analysis Result
        db.analysis_results.update_one(
            {"entity_id": entity_id},
            {
                "$inc": {
                    f"results.{sentiment_label}_count": 1,
                    "results.total_comments": 1,
                },
                "$setOnInsert": {
                    "entity_id": entity_id,
                    "analysis_type": "weekly",
                    "created_at": datetime.now(),
                    "status": "completed",
                },
            },
            upsert=True,
        )

    # 3e. Bulk insert all comments from the batch
    if comments_to_insert:
        db.comments_youtube.insert_many(comments_to_insert)
        print(f"Inserted {len(comments_to_insert)} raw comments into database.")


def run_consumer_job() -> None:
    """
    This job consumes raw comments from Kafka in batches, performs sentiment analysis,
    and saves the results into MongoDB.
    """
    # --- 1. Initialization ---
    print("Initializing services...")
    sentiment_service = SentimentService()
    mongo_client = MongoClient(settings.MONGODB_CONNECTION_STRING)
    db = mongo_client[settings.DB_NAME]

    kafka_conf = {
        "bootstrap.servers": "localhost:9092",
        "group.id": "sentiment_analyzer_group",
        "auto.offset.reset": "earliest",
    }
    consumer = Consumer(kafka_conf)
    consumer.subscribe([settings.KAFKA_TOPIC])

    print("Consumer job started. Waiting for messages...")

    # --- 2. Batch Processing Loop ---
    message_batch: List[Message] = []
    last_process_time = time.time()

    try:
        while True:
            msg = consumer.poll(timeout=1.0)

            if msg is None:
                # No new message, check for timeout
                if message_batch and (
                    time.time() - last_process_time
                    > settings.CONSUMER_BATCH_TIMEOUT_SECONDS
                ):
                    process_message_batch(message_batch, sentiment_service, db)
                    message_batch.clear()
                    last_process_time = time.time()
                continue

            if msg.error():
                # Handle Kafka errors
                if msg.error().code() != KafkaError._PARTITION_EOF:
                    print(f"Kafka error: {msg.error()}")
                continue

            # Add message to batch and check if batch is full
            message_batch.append(msg)
            if len(message_batch) >= settings.CONSUMER_BATCH_SIZE:
                process_message_batch(message_batch, sentiment_service, db)
                message_batch.clear()
                last_process_time = time.time()

    except KeyboardInterrupt:
        print("Stopping consumer job...")
        # Process any remaining messages in the batch before exiting
        process_message_batch(message_batch, sentiment_service, db)
    finally:
        consumer.close()
        mongo_client.close()
        print("Consumer and DB connection closed.")


if __name__ == "__main__":
    run_consumer_job()
