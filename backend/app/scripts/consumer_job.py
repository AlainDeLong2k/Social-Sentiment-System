import json
import time
import torch
from typing import Dict, Any, List
from pymongo import MongoClient
from pymongo.database import Database
from bson.objectid import ObjectId
from confluent_kafka import Consumer, KafkaError, Message
from transformers import pipeline, Pipeline
from app.core.config import settings
from datetime import datetime


def preprocess_text(text: str) -> str:
    """
    Preprocesses text by replacing @user mentions and http links with placeholders,
    as recommended by the sentiment model's authors.
    """
    if not isinstance(text, str):
        return ""
    new_text = []
    for t in text.split(" "):
        t = "@user" if t.startswith("@") and len(t) > 1 else t
        t = "http" if t.startswith("http") else t
        new_text.append(t)
    return " ".join(new_text)


def load_sentiment_model() -> Pipeline:
    """
    Checks for GPU availability and loads the sentiment analysis model.
    """
    device_index = 0 if torch.cuda.is_available() else -1
    if device_index == 0:
        print(f"GPU found: {torch.cuda.get_device_name(0)}. Loading model onto GPU.")
    else:
        print("GPU not found. Loading model onto CPU.")

    model_name = "cardiffnlp/twitter-roberta-base-sentiment-latest"
    sentiment_pipeline = pipeline(
        "sentiment-analysis",
        model=model_name,
        tokenizer=model_name,
        device=device_index,
        max_length=512,
        padding="max_length",
        truncation=True,
    )
    print("Sentiment model loaded successfully.")
    return sentiment_pipeline


# def process_message_batch(
#     batch: List[Message], sentiment_pipeline: Pipeline, db: Database
# ) -> None:
#     """
#     Processes a batch of Kafka messages: performs sentiment analysis and updates the database.
#     """
#     if not batch:
#         return

#     print(f"Processing a batch of {len(batch)} messages...")

#     # --- 1. Prepare data for the model ---
#     messages_data: List[Dict[str, Any]] = []
#     texts_to_predict: List[str] = []

#     for msg in batch:
#         message_data = json.loads(msg.value().decode("utf-8"))
#         original_text = message_data.get("comment_data", {}).get("text", "")
#         preprocessed_text = preprocess_text(original_text)

#         # Only add non-empty texts to the prediction list
#         if preprocessed_text.strip():
#             messages_data.append(message_data)
#             texts_to_predict.append(preprocessed_text)

#     if not texts_to_predict:
#         print("Batch contains only empty comments after preprocessing. Skipping.")
#         return

#     # --- 2. Perform Batch Sentiment Analysis ---
#     predictions = sentiment_pipeline(texts_to_predict)

#     # --- 3. Perform Batch Database Operations ---
#     for message_data, prediction in zip(messages_data, predictions):
#         entity_keyword = message_data.get("entity_keyword")
#         entity_thumbnail = message_data.get("entity_thumbnail_url")
#         entity_volume = message_data.get("entity_volume")
#         sentiment_label = prediction["label"].lower()

#         if not all([entity_keyword, entity_volume is not None]):
#             continue

#         # Upsert Entity to get its ID
#         entity_doc = db.entities.find_one_and_update(
#             {"keyword": entity_keyword},
#             {
#                 "$setOnInsert": {
#                     "keyword": entity_keyword,
#                     "geo": settings.FETCH_TRENDS_GEO,
#                     "volume": entity_volume,
#                     "thumbnail_url": entity_thumbnail,
#                     "start_date": datetime.now(),
#                 }
#             },
#             upsert=True,
#             return_document=True,
#         )
#         entity_id = entity_doc["_id"]

#         # Upsert and update Analysis Result
#         db.analysis_results.update_one(
#             {"entity_id": entity_id},
#             {
#                 "$inc": {
#                     f"results.{sentiment_label}_count": 1,
#                     "results.total_comments": 1,
#                 },
#                 "$setOnInsert": {
#                     "entity_id": entity_id,
#                     "analysis_type": "weekly",
#                     "created_at": datetime.now(),
#                     "status": "completed",
#                 },
#             },
#             upsert=True,
#         )


def process_message_batch(
    batch: List[Message], sentiment_pipeline: Pipeline, db: Database
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
        original_text = message_data.get("video_and_comment_data", {}).get("text", "")
        preprocessed_text = preprocess_text(original_text)

        if preprocessed_text.strip():
            messages_data.append(message_data)
            texts_to_predict.append(preprocessed_text)

    if not texts_to_predict:
        print("Batch contains only empty comments after preprocessing. Skipping.")
        return

    # --- 2. Perform Batch Sentiment Analysis ---
    predictions = sentiment_pipeline(texts_to_predict)

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
    sentiment_pipeline = load_sentiment_model()
    mongo_client = MongoClient(settings.MONGODB_CONNECTION_STRING)
    db = mongo_client["sentiment_analysis_db"]

    kafka_conf = {
        "bootstrap.servers": "localhost:9092",
        "group.id": "sentiment_analyzer_group",
        "auto.offset.reset": "earliest",
    }
    consumer = Consumer(kafka_conf)
    # consumer.subscribe(["raw_youtube_comments"])
    consumer.subscribe(["test-topic"])

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
                    process_message_batch(message_batch, sentiment_pipeline, db)
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
                process_message_batch(message_batch, sentiment_pipeline, db)
                message_batch.clear()
                last_process_time = time.time()

    except KeyboardInterrupt:
        print("Stopping consumer job...")
        # Process any remaining messages in the batch before exiting
        process_message_batch(message_batch, sentiment_pipeline, db)
    finally:
        consumer.close()
        mongo_client.close()
        print("Consumer and DB connection closed.")


# def run_consumer_job() -> None:
#     """
#     This job consumes raw comments from Kafka, performs sentiment analysis,
#     and saves the structured results into MongoDB collections.
#     """
#     # --- 1. Initialization ---
#     sentiment_pipeline = load_sentiment_model()

#     mongo_client = MongoClient(settings.MONGODB_CONNECTION_STRING)
#     db = mongo_client["sentiment_analysis_db"]  # Use the DB name from init_db script

#     kafka_conf = {
#         "bootstrap.servers": "localhost:9092",
#         "group.id": "sentiment_analyzer_group",
#         "auto.offset.reset": "earliest",  # Start reading from the beginning of the topic
#     }
#     consumer = Consumer(kafka_conf)
#     # consumer.subscribe(["raw_youtube_comments"])
#     consumer.subscribe(["test-topic"])

#     print("Consumer job started. Waiting for messages...")

#     # --- 2. Main Processing Loop ---
#     try:
#         while True:
#             msg = consumer.poll(timeout=1.0)  # Wait for 1 second for a message

#             if msg is None:
#                 continue
#             if msg.error():
#                 if msg.error().code() == KafkaError._PARTITION_EOF:
#                     # End of partition event
#                     print("Reached end of partition, but will continue listening.")
#                 else:
#                     print(f"Kafka error: {msg.error()}")
#                 continue

#             # --- 3. Message Processing ---
#             message_data: Dict[str, Any] = json.loads(msg.value().decode("utf-8"))
#             entity_keyword = message_data.get("entity_keyword")
#             entity_thumbnail = message_data.get("entity_thumbnail_url")
#             entity_volume = message_data.get("entity_volume")
#             comment_data = message_data.get("comment_data", {})

#             if not all([entity_keyword, comment_data, entity_volume is not None]):
#                 print("Skipping message with missing data.")
#                 continue

#             # --- 4. Sentiment Analysis ---
#             original_text = comment_data.get("text", "")
#             preprocessed_text = preprocess_text(original_text)

#             if not preprocessed_text.strip():
#                 continue  # Skip empty comments after preprocessing

#             prediction = sentiment_pipeline(preprocessed_text)[0]
#             sentiment_label = prediction[
#                 "label"
#             ].lower()  # Should be 'positive', 'neutral', or 'negative'

#             # --- 5. Database Operations ---
#             # 5a. Upsert Entity and get its ID
#             entity_doc = db.entities.find_one_and_update(
#                 {"keyword": entity_keyword},
#                 {
#                     "$setOnInsert": {
#                         "keyword": entity_keyword,
#                         "geo": settings.FETCH_TRENDS_GEO,
#                         "volume": entity_volume,
#                         "thumbnail_url": entity_thumbnail,
#                         "start_date": datetime.now(),  # Approximate start date
#                     }
#                 },
#                 upsert=True,
#                 return_document=True,
#             )
#             entity_id = entity_doc["_id"]

#             # 5b. Upsert and update Analysis Result
#             # ... (inside the `while True:` loop, after sentiment analysis)

#             # --- 5b. Upsert and update Analysis Result (FINAL AND SIMPLEST FIX) ---
#             db.analysis_results.update_one(
#                 {"entity_id": entity_id},
#                 {
#                     # $inc will create the fields if they don't exist, and increment them if they do.
#                     "$inc": {
#                         f"results.{sentiment_label}_count": 1,
#                         "results.total_comments": 1,
#                     },
#                     # $setOnInsert will only set these top-level fields when the document is first created.
#                     "$setOnInsert": {
#                         "entity_id": entity_id,
#                         "analysis_type": "weekly",
#                         "created_at": datetime.now(),
#                         "status": "completed",
#                     },
#                 },
#                 upsert=True,
#             )

#     except KeyboardInterrupt:
#         print("Stopping consumer job.")
#     finally:
#         consumer.close()
#         mongo_client.close()
#         print("Consumer and DB connection closed.")


if __name__ == "__main__":
    run_consumer_job()
