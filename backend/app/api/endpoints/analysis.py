from typing import Any, List, Dict
import uuid
import time
from datetime import datetime
from fastapi import APIRouter, HTTPException, status, Request

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

import pandas as pd
from trendspy import Trends

from app.core.config import settings
from app.core.clients import qstash_client
from app.core.exceptions import QuotaExceededError
from app.schemas.analysis_schema import (
    WeeklyTrendListResponse,
    TrendDetailResponseSchema,
    OnDemandRequestSchema,
    OnDemandResponseSchema,
    JobStatusResponseSchema,
)
from app.services.sentiment_service import SentimentService
from app.services.youtube_service import YouTubeService

# Create a router to organize endpoints
# router = APIRouter(prefix="/trends", tags=["trends"])
router = APIRouter(prefix=settings.API_PREFIX_TRENDS)

# --- MongoDB Connection ---
client = AsyncIOMotorClient(settings.MONGODB_CONNECTION_STRING)
db = client[settings.DB_NAME]

# Initialize services once when the application starts.
# This avoids reloading the heavy AI model on every request.
print("Initializing services...")
tr = Trends(request_delay=2.0)
yt_service = YouTubeService(api_key=settings.YT_API_KEY)
sentiment_service = SentimentService()


async def fetch_repr_comments(entity_id):
    # Find all source videos linked to this entity
    source_docs = await db.sources_youtube.find({"entity_id": entity_id}).to_list(
        length=None
    )
    source_ids = [doc["_id"] for doc in source_docs]

    if not source_ids:
        return {"positive": [], "neutral": [], "negative": []}

    # Fetch newest comments for each sentiment
    sentiments = ["positive", "neutral", "negative"]
    comment_tasks = []
    limit = settings.REPRESENTATIVE_COMMENTS_LIMIT
    for sentiment in sentiments:
        task = (
            db.comments_youtube.find(
                {"source_id": {"$in": source_ids}, "sentiment": sentiment},
                {"text": 1, "author": 1, "publish_date": 1, "_id": 0},
            )
            .sort("publish_date", -1)
            .limit(limit)
            .to_list(length=limit)
        )

        comment_tasks.append(task)

    results = await asyncio.gather(*comment_tasks)
    # Convert datetime objects to string format for JSON response
    for sentiment_list in results:
        for comment in sentiment_list:
            if "publish_date" in comment and hasattr(
                comment["publish_date"], "isoformat"
            ):
                comment["publish_date"] = comment["publish_date"].isoformat()

    return dict(zip(sentiments, results))


async def _get_full_entity_details(
    entity_id: ObjectId, analysis_type: str
) -> Dict[str, Any] | None:
    """
    Fetches all detailed data for an entity. It runs the database query,
    interest data fetching, and comment fetching as concurrent, independent tasks.
    """

    async def fetch_main_data_task():
        """Fetches the main analysis data from the database."""
        pipeline = [
            {"$match": {"entity_id": entity_id, "analysis_type": analysis_type}},
            {"$sort": {"created_at": -1}},
            {"$limit": 1},
            {
                "$lookup": {
                    "from": "entities",
                    "localField": "entity_id",
                    "foreignField": "_id",
                    "as": "entity_info",
                }
            },
            {"$unwind": "$entity_info"},
            {
                "$project": {
                    "analysis_result_id": "$_id",
                    "_id": {"$toString": "$entity_info._id"},
                    "keyword": "$entity_info.keyword",
                    "thumbnail_url": "$entity_info.thumbnail_url",
                    "representative_video_url": "$entity_info.video_url",
                    "analysis": "$results",
                    "interest_over_time": "$interest_over_time",
                }
            },
        ]
        results = await db.analysis_results.aggregate(pipeline).to_list(length=1)
        return results[0] if results else None

    # Run the main DB query and comment fetching concurrently
    main_data_task = fetch_main_data_task()
    comments_task = fetch_repr_comments(entity_id)

    main_data, rep_comments = await asyncio.gather(main_data_task, comments_task)

    if not main_data:
        # If the main entity/analysis is not found, we can't proceed.
        return None

    # Now, handle the interest data fetching based on the result of the main query
    if not main_data.get("interest_over_time"):
        print(
            f"Interest data not found in DB for '{main_data['keyword']}'. Fetching live..."
        )

        def blocking_interest_fetch(keyword: str):
            """Synchronous wrapper for the blocking trendspy call."""
            df = tr.interest_over_time(keywords=[keyword], timeframe="now 7-d")
            if df.empty:
                return []
            daily_df = df[[keyword]].resample("D").mean().round(0).astype(int)
            return [
                {"date": index.strftime("%Y-%m-%d"), "value": int(row.iloc[0])}
                for index, row in daily_df.iterrows()
            ]

        try:
            # Run the blocking call in a separate thread to not block the server
            interest_data_to_cache = await asyncio.to_thread(
                blocking_interest_fetch, main_data["keyword"]
            )

            if interest_data_to_cache:
                main_data["interest_over_time"] = interest_data_to_cache
                await db.analysis_results.update_one(
                    {"_id": main_data["analysis_result_id"]},
                    {"$set": {"interest_over_time": interest_data_to_cache}},
                )
                print(
                    f"Successfully cached interest data for '{main_data['keyword']}'."
                )
        except Exception as e:
            print(f"Could not fetch live interest data: {e}")
            main_data["interest_over_time"] = []

    # Combine all results
    main_data.pop("analysis_result_id", None)
    return {**main_data, "representative_comments": rep_comments}


@router.get("/weekly", response_model=WeeklyTrendListResponse)
async def get_weekly_trends():
    """
    Retrieves the latest weekly sentiment analysis results.

    This endpoint fetches data from the 'analysis_results' collection and
    joins it with the 'entities' collection to get keyword and thumbnail details.
    """
    try:
        # MongoDB Aggregation Pipeline to join collections
        pipeline = [
            # 1. Filter for weekly analysis and sort by date to get the latest run
            {"$match": {"analysis_type": "weekly"}},
            {"$sort": {"created_at": -1}},
            {"$limit": settings.HOME_PAGE_ENTITIES_LIMIT},
            # 2. Join with the 'entities' collection
            {
                "$lookup": {
                    "from": "entities",
                    "localField": "entity_id",
                    "foreignField": "_id",
                    "as": "entity_info",
                }
            },
            # 3. Deconstruct the entity_info array
            {"$unwind": "$entity_info"},
            # 4. Project the final structure for the API response
            {
                "$project": {
                    "_id": {"$toString": "$entity_info._id"},
                    "keyword": "$entity_info.keyword",
                    "thumbnail_url": "$entity_info.thumbnail_url",
                    "analysis": {
                        "positive_count": "$results.positive_count",
                        "negative_count": "$results.negative_count",
                        "neutral_count": "$results.neutral_count",
                        "total_comments": "$results.total_comments",
                    },
                }
            },
        ]

        results = await db.analysis_results.aggregate(pipeline).to_list(length=None)
        if not results:
            raise HTTPException(status_code=500, detail="Internal server error")

        response_data = {"data": results}
        return response_data

    except Exception as e:
        # Log the error for debugging
        print(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{analysis_type}/{entity_id}", response_model=TrendDetailResponseSchema)
async def get_trend_detail_by_type(analysis_type: str, entity_id: str):
    """
    Retrieves detailed information for a single entity, specifying
    whether to fetch the 'weekly' or 'on-demand' analysis result.
    """
    if analysis_type not in ["weekly", "on-demand"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid analysis type. Must be 'weekly' or 'on-demand'.",
        )

    try:
        entity_obj_id = ObjectId(entity_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid entity ID format.")

    # Call the helper function with the specified type
    full_details = await _get_full_entity_details(entity_obj_id, analysis_type)

    if not full_details:
        raise HTTPException(
            status_code=404,
            detail=f"'{analysis_type}' analysis for this entity not found.",
        )

    return full_details


@router.post(
    "/analysis/on-demand",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=OnDemandResponseSchema,
)
async def create_on_demand_analysis(request_data: OnDemandRequestSchema):
    """
    Handles an on-demand analysis request.
    First, it checks if a recent 'weekly' analysis for the keyword exists.
    If yes, it returns a 'found' status with the entity_id for immediate redirection.
    If not, it queues a new analysis job via QStash and returns a 'queued' status.
    """
    if not request_data.keyword or not request_data.keyword.strip():
        raise HTTPException(status_code=400, detail="Keyword cannot be empty.")

    # Convert incoming keyword to lowercase for consistent matching
    keyword = request_data.keyword.lower().strip()

    # Check for existing weekly analysis
    entity = await db.entities.find_one({"keyword": keyword})
    if entity:
        analysis = await db.analysis_results.find_one(
            {"entity_id": entity["_id"], "analysis_type": "weekly"}
        )
        if analysis:
            print(
                f"Found existing weekly analysis for '{keyword}'. Returning redirect info."
            )
            # Return a different response if data already exists
            return {"status": "found", "entity_id": str(entity["_id"])}

    # If no existing analysis, proceed with queuing a new job
    print(f"No weekly analysis found for '{keyword}'. Queuing a new job.")

    job_id = str(uuid.uuid4())

    job_document = {
        "_id": job_id,
        "keyword": keyword,
        "status": "pending",
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
        "result_id": None,
    }
    await db.on_demand_jobs.insert_one(job_document)

    # callback_url = f"{settings.BASE_URL}/api/v1/trends/analysis/process-job"
    callback_url = f"{settings.BASE_URL}{settings.API_PREFIX}{settings.API_VERSION}{settings.API_PREFIX_TRENDS}/analysis/process-job"

    print(
        f"Queuing job {job_id} for keyword '{keyword}' with callback to {callback_url}"
    )

    try:
        qstash_client.message.publish_json(
            url=callback_url, body={"keyword": keyword, "job_id": job_id}, retries=0
        )
    except Exception as e:
        # If publishing fails, update the job status to 'failed'
        await db.on_demand_jobs.update_one(
            {"_id": job_id}, {"$set": {"status": "failed"}}
        )
        print(f"Error publishing to QStash: {e}")
        raise HTTPException(status_code=500, detail="Failed to queue analysis job.")

    return {"status": "queued", "job_id": job_id}


@router.get("/analysis/status/{job_id}", response_model=JobStatusResponseSchema)
async def get_analysis_status(job_id: str):
    """
    Checks the status of an on-demand analysis job from the 'on_demand_jobs' collection.
    If complete or failed, it returns the final result or an error message.
    """
    job = await db.on_demand_jobs.find_one({"_id": job_id})

    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")

    response_data = {
        "_id": job["_id"],
        "status": job["status"],
        "keyword": job["keyword"],
        "result": None,
        "error_message": job.get("error_message"),
    }

    # If job is completed, fetch the full result data
    if job["status"] == "completed" and job.get("result_id"):
        analysis_doc = await db.analysis_results.find_one({"_id": job["result_id"]})

        # Check if the analysis document exists and contains an entity_id
        if analysis_doc and analysis_doc.get("entity_id"):
            # Get the correct entity_id from the analysis document
            entity_id = analysis_doc["entity_id"]

            # Call the helper with the correct entity_id and type
            full_details = await _get_full_entity_details(entity_id, "on-demand")
            response_data["result"] = full_details

    return response_data


@router.post("/analysis/process-job", include_in_schema=False)
async def process_on_demand_job(request: Request):
    """
    A webhook endpoint called by QStash to perform the full analysis for a
    single keyword. It fetches data, runs sentiment analysis, and saves all
    results to the database.
    """
    start = time.perf_counter()

    # 1. Initialization
    job_data = await request.json()
    print(job_data)
    keyword = job_data.get("keyword")
    job_id = job_data.get("job_id")

    if not job_id:
        raise HTTPException(status_code=400, detail="Job ID is missing.")

    if not keyword:
        # Acknowledge the request but do nothing if keyword is missing
        # If we have a job_id but no keyword, mark the job as failed.
        await db.on_demand_jobs.update_one(
            {"_id": job_id},
            {"$set": {"status": "failed", "updated_at": datetime.now()}},
        )
        raise HTTPException(status_code=400, detail="Keyword is missing, job ignored.")

    # Update job status to 'processing'
    await db.on_demand_jobs.update_one(
        {"_id": job_id},
        {"$set": {"status": "processing", "updated_at": datetime.now()}},
    )
    print(f"Processing job {job_id} for keyword: {keyword}")

    try:
        # 2. Fetch data (similar to a mini-producer)
        # Note: For on-demand, I might use a smaller fetching strategy
        videos = yt_service.search_videos(query_string=keyword)
        if not videos:
            error_msg: str = f"No videos found for on-demand keyword '{keyword}'."
            print(error_msg)

            # Update job status to failed and raise an exception
            await db.on_demand_jobs.update_one(
                {"_id": job_id},
                {
                    "$set": {
                        "status": "failed",
                        "error_message": error_msg,
                        "updated_at": datetime.now(),
                    }
                },
            )
            raise HTTPException(
                status_code=404,
                detail=error_msg,
            )

        comments_for_entity: List[Dict[str, Any]] = []
        for video in videos:
            video_id = video.get("id", {}).get("videoId")
            snippet = video.get("snippet", {})
            if not video_id or not snippet:
                continue

            comments = yt_service.fetch_comments(
                video_id=video_id, limit=settings.ON_DEMAND_COMMENTS_PER_VIDEO
            )  # Smaller limit for on-demand

            for comment in comments:
                comment["video_id"] = video_id
                comment["video_title"] = snippet.get("title")
                comment["video_publish_date"] = snippet.get("publishedAt")
                comment["video_url"] = f"https://www.youtube.com/watch?v={video_id}"
            comments_for_entity.extend(comments)

            if (
                len(comments_for_entity) >= settings.ON_DEMAND_TOTAL_COMMENTS
            ):  # Smaller total limit for on-demand
                break

        final_comments = comments_for_entity[: settings.ON_DEMAND_TOTAL_COMMENTS]
        if not final_comments:
            error_msg = f"No comments found for on-demand keyword '{keyword}'."
            print(error_msg)

            # Update job status to failed and raise an exception
            await db.on_demand_jobs.update_one(
                {"_id": job_id},
                {
                    "$set": {
                        "status": "failed",
                        "error_message": error_msg,
                        "updated_at": datetime.now(),
                    }
                },
            )
            raise HTTPException(status_code=404, detail=error_msg)

        # 3. Perform Sentiment Analysis
        print(f"Analyzing {len(final_comments)} comments in batches...")
        texts_to_predict = [comment.get("text", "") for comment in final_comments]
        predictions = sentiment_service.predict(texts_to_predict)
        print(f"Successfully analyzed {len(final_comments)} comments!!!")

        # 4. Save raw data and aggregate counts in memory to Database (similar to a mini-consumer)

        # 4a. Upsert Entity first to get a stable entity_id
        video_id = videos[0].get("id", {}).get("videoId", "")
        entity_video_url = f"https://www.youtube.com/watch?v={video_id}"
        entity_thumbnail_url = (
            videos[0]
            .get("snippet", {})
            .get("thumbnails", {})
            .get("high", {})
            .get("url")
        )

        entity_doc = await db.entities.find_one_and_update(
            {"keyword": keyword},
            {
                "$set": {
                    "thumbnail_url": entity_thumbnail_url,
                    "video_url": entity_video_url,
                },
                "$setOnInsert": {
                    "keyword": keyword,
                    "geo": settings.FETCH_TRENDS_GEO,
                    "volume": 0,  # Placeholder values
                    "start_date": datetime.now(),
                },
            },
            upsert=True,
            return_document=True,
        )
        entity_id = entity_doc["_id"]

        # 4b. Process and save each comment
        # Initialize in-memory counters
        sentiment_counts = {"positive": 0, "negative": 0, "neutral": 0}

        video_id_cache: Dict[str, ObjectId] = {}
        comments_to_insert: List[Dict[str, Any]] = []

        for comment_data, prediction in zip(final_comments, predictions):
            sentiment_label = prediction["label"].lower()

            # Increment the counter in memory instead of calling the DB
            sentiment_counts[sentiment_label] += 1

            # Upsert Source Video
            video_id = comment_data.get("video_id")
            source_id: ObjectId | None = video_id_cache.get(video_id)
            if not source_id:
                source_doc = await db.sources_youtube.find_one_and_update(
                    {"video_id": video_id},
                    {
                        "$set": {"entity_id": entity_id},
                        "$setOnInsert": {
                            "video_id": video_id,
                            "url": comment_data.get("video_url"),
                            "title": comment_data.get("video_title"),
                            "publish_date": datetime.strptime(
                                comment_data.get("video_publish_date"),
                                "%Y-%m-%dT%H:%M:%SZ",
                            ),
                        },
                    },
                    upsert=True,
                    return_document=True,
                )
                source_id = source_doc["_id"]
                video_id_cache[video_id] = source_id

            # Prepare comment for bulk insertion
            comments_to_insert.append(
                {
                    "source_id": source_id,
                    "comment_id": comment_data.get("comment_id"),
                    "text": comment_data.get("text"),
                    "author": comment_data.get("author"),
                    "publish_date": datetime.strptime(
                        comment_data.get("publish_date"), "%Y-%m-%dT%H:%M:%SZ"
                    ),
                    "sentiment": sentiment_label,
                }
            )

        # 4c. Bulk insert all comments after the loop
        if comments_to_insert:
            await db.comments_youtube.insert_many(comments_to_insert)

        # 4d. Update analysis_results only ONCE with the final aggregated counts
        analysis_result_doc = await db.analysis_results.find_one_and_update(
            {"entity_id": entity_id, "analysis_type": "on-demand"},
            {
                "$inc": {
                    "results.positive_count": sentiment_counts["positive"],
                    "results.negative_count": sentiment_counts["negative"],
                    "results.neutral_count": sentiment_counts["neutral"],
                    "results.total_comments": len(final_comments),
                },
                "$setOnInsert": {
                    "entity_id": entity_id,
                    "analysis_type": "on-demand",
                    "created_at": datetime.now(),
                    "status": "processing",
                    "interest_over_time": [],
                },
            },
            upsert=True,
            return_document=True,
        )
        result_id = analysis_result_doc["_id"]

        # 4e. Final update to job status
        await db.on_demand_jobs.update_one(
            {"_id": job_id},
            {
                "$set": {
                    "status": "completed",
                    "result_id": result_id,
                    "updated_at": datetime.now(),
                }
            },
        )
    except QuotaExceededError as e:  # Catch the specific QuotaExceededError
        error_msg = str(e)
        print(f"Quota exceeded for job {job_id}: {error_msg}")
        await db.on_demand_jobs.update_one(
            {"_id": job_id},
            {
                "$set": {
                    "status": "failed",
                    "error_message": error_msg,
                    "updated_at": datetime.now(),
                }
            },
        )

        # Raise a generic exception to QStash
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=error_msg
        )
    except Exception as e:  # The general exception handler set a message
        # Use the actual exception message for the error_message
        error_msg = str(e)
        print(f"An error occurred processing job {job_id}: {error_msg}")
        await db.on_demand_jobs.update_one(
            {"_id": job_id},
            {
                "$set": {
                    "status": "failed",
                    "error_message": error_msg,
                    "updated_at": datetime.now(),
                }
            },
        )

        # Raise a generic exception to QStash
        raise HTTPException(
            status_code=500, detail="An internal processing error occurred."
        )

    end = time.perf_counter()
    print(
        f"Successfully processed and saved analysis for job {job_id} in {end-start:.6f}"
    )
    return {"message": f"Job {job_id} for '{keyword}' processed successfully."}
