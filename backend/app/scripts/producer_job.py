import json
from typing import Any, List, Dict
from datetime import datetime as dt, timedelta
from trendspy import Trends
from confluent_kafka import Producer

from app.core.config import settings
from app.services.youtube_service import YouTubeService


def get_rfc_time_ago(days: int) -> str:
    """
    Calculates the datetime N days ago from now and returns it in RFC 3339 format.
    """
    time_ago = dt.now() - timedelta(days=days)
    return time_ago.strftime("%Y-%m-%dT%H:%M:%SZ")


def run_producer_job() -> None:
    """
    This job fetches trending topics, searches for related YouTube videos,
    collects comments from those videos, and sends them to a Kafka topic.
    It uses a contextual query building strategy for better search accuracy.
    """
    # --- 1. Initialization ---
    yt_service = YouTubeService(api_key=settings.YT_API_KEY)

    kafka_conf = {"bootstrap.servers": "localhost:9092"}
    producer = Producer(kafka_conf)

    kafka_topic = settings.KAFKA_TOPIC
    print("Producer job started...")

    # --- 2. Get Trending Entities ---
    try:
        trends_client = Trends()
        trends = trends_client.trending_now(
            geo=settings.FETCH_TRENDS_GEO, hours=24 * settings.FETCH_TRENDS_WITHIN_DAYS
        )
        trends.sort(key=lambda item: item.volume, reverse=True)
        top_trends = trends[: settings.FETCH_NUM_ENTITIES]
        print(f"Successfully fetched {len(top_trends)} trending entities.")
    except Exception as e:
        print(f"Failed to fetch trends: {e}")
        return

    time_filter = get_rfc_time_ago(days=settings.FETCH_TRENDS_WITHIN_DAYS)

    # --- 3. Process Each Entity ---
    for trend in top_trends:
        entity_keyword = trend.keyword
        print(f"\n--- Processing entity: {entity_keyword} ---")

        # --- 3a. Contextual Query Building ---
        # Sort related keywords by length to prioritize more specific ones
        related_keywords = sorted(trend.trend_keywords, key=len, reverse=True)
        # Combine the main keyword with the top 2 longest related keywords
        keywords_to_search = [entity_keyword] + related_keywords[:2]
        # Remove duplicates
        keywords_to_search = list(dict.fromkeys(keywords_to_search))
        # Create a query like: '"long keyword" OR "main keyword"'
        query_string = " OR ".join([f'"{k}"' for k in keywords_to_search])

        print(f"Constructed query: {query_string}")

        # --- 3b. Search and Get Thumbnail ---
        videos = yt_service.search_videos(
            query_string=query_string, published_after=time_filter
        )

        if not videos:
            print(f"No videos found for '{entity_keyword}'. Skipping...")
            continue

        # entity_thumbnail_url = (
        #     videos[0]
        #     .get("snippet", {})
        #     .get("thumbnails", {})
        #     .get("high", {})
        #     .get("url")
        # )

        first_video = videos[0] # NEW
        entity_thumbnail_url = first_video.get("snippet", {}).get("thumbnails", {}).get("high", {}).get("url")
        # NEW: Construct the representative video URL
        video_id = first_video.get("id", {}).get("videoId", "")
        entity_video_url = f"https://www.youtube.com/watch?v={video_id}" if video_id else None


        # --- 3c. Fetch Comments with Smart Sampling ---
        comments_for_entity: List[Dict[str, Any]] = []
        for video in videos:
            video_id = video.get("id", {}).get("videoId")
            snippet = video.get("snippet", {})
            if not video_id or not snippet:
                continue

            print(
                f"Fetching comments from video: {snippet.get('title', 'N/A')[:50]}..."
            )
            comments = yt_service.fetch_comments(
                video_id=video_id, limit=settings.FETCH_COMMENTS_PER_VIDEO
            )

            for comment in comments:
                comment["video_id"] = video_id
                comment["video_title"] = snippet.get("title")
                comment["video_publish_date"] = snippet.get("publishedAt")
                comment["video_url"] = f"https://www.youtube.com/watch?v={video_id}"

            comments_for_entity.extend(comments)

            if len(comments_for_entity) >= settings.FETCH_TOTAL_COMMENTS_PER_ENTITY:
                break

        final_comments = comments_for_entity[: settings.FETCH_TOTAL_COMMENTS_PER_ENTITY]

        # --- 4. Produce Messages to Kafka ---
        if not final_comments:
            print(f"No comments collected for '{entity_keyword}'.")
            continue

        print(
            f"Producing {len(final_comments)} comments for '{entity_keyword}' to Kafka topic '{kafka_topic}'..."
        )
        for comment in final_comments:
            message_payload = {
                "entity_keyword": entity_keyword,
                "entity_thumbnail_url": entity_thumbnail_url,
                "entity_video_url": entity_video_url,
                "entity_volume": trend.volume,
                "video_and_comment_data": comment,
            }
            producer.produce(
                kafka_topic,
                key=entity_keyword.encode("utf-8"),
                value=json.dumps(message_payload).encode("utf-8"),
            )

    producer.flush()
    print("\nProducer job finished. All messages flushed to Kafka.")


if __name__ == "__main__":
    run_producer_job()
