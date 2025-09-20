from typing import List, Dict
from requests import HTTPError
from fastapi import APIRouter, HTTPException

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

import pandas as pd
from trendspy import Trends

from app.core.config import settings
from app.schemas.analysis_schema import WeeklyTrendResponseSchema, TrendDetailResponseSchema

# Create a router to organize endpoints
# router = APIRouter(prefix="/trends", tags=["trends"])
router = APIRouter(prefix="/trends")

# --- MongoDB Connection ---
client = AsyncIOMotorClient(settings.MONGODB_CONNECTION_STRING)
db = client[settings.DB_NAME]

tr = Trends(request_delay=2.0)


@router.get("/weekly", response_model=List[WeeklyTrendResponseSchema])
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
            {
                '$match': {'analysis_type': 'weekly'}
            },
            {
                '$sort': {'created_at': -1}
            },
            # This is a simplified way to get the latest. A more robust way would involve grouping.
            # For the scope of this project, we assume the latest documents are from the last run.
            {
                '$limit': settings.FETCH_NUM_ENTITIES
            },
            # 2. Join with the 'entities' collection
            {
                '$lookup': {
                    'from': 'entities',
                    'localField': 'entity_id',
                    'foreignField': '_id',
                    'as': 'entity_info'
                }
            },
            # 3. Deconstruct the entity_info array
            {
                '$unwind': '$entity_info'
            },
            # 4. Project the final structure for the API response
            {
                '$project': {
                    '_id': {'$toString': '$entity_info._id'},
                    'keyword': '$entity_info.keyword',
                    'thumbnail_url': '$entity_info.thumbnail_url',
                    'analysis': {
                        'positive_count': '$results.positive_count',
                        'negative_count': '$results.negative_count',
                        'neutral_count': '$results.neutral_count',
                        'total_comments': '$results.total_comments'
                    }
                }
            }
        ]

        results = await db.analysis_results.aggregate(pipeline).to_list(length=None)

        if not results:
            return []

        return results

    except Exception as e:
        # Log the error for debugging
        print(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{entity_id}", response_model=TrendDetailResponseSchema)
async def get_trend_detail(entity_id: str):
    """
    Retrieves all detailed information for a single entity, including
    analysis results, representative comments, and interest over time data.
    """
    try:
        # Validate the provided ID
        entity_obj_id = ObjectId(entity_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid entity ID format.")

    # 1. Fetch main entity data and analysis results
    entity_pipeline = [
        {'$match': {'_id': entity_obj_id}},
        {'$lookup': {
            'from': 'analysis_results',
            'localField': '_id',
            'foreignField': 'entity_id',
            'as': 'analysis_info'
        }},
        {'$unwind': '$analysis_info'},
        {'$project': {
            '_id': {'$toString': '$_id'},
            'keyword': '$keyword',
            'thumbnail_url': '$thumbnail_url',
            'analysis': {
                'positive_count': '$analysis_info.results.positive_count',
                'negative_count': '$analysis_info.results.negative_count',
                'neutral_count': '$analysis_info.results.neutral_count',
                'total_comments': '$analysis_info.results.total_comments'
            }
        }}
    ]
    main_data_list = await db.entities.aggregate(entity_pipeline).to_list(length=1)
    if not main_data_list:
        raise HTTPException(status_code=404, detail='Entity not found.')
    main_data = main_data_list[0]
    print(main_data_list)

    # 2. Asynchronously fetch representative comments and interest data
    async def fetch_repr_comments():
        # Find all source videos linked to this entity
        source_docs = await db.sources_youtube.find({'entity_id': entity_obj_id}).to_list(length=None)
        source_ids = [doc['_id'] for doc in source_docs]

        if not source_ids:
            return {"positive": [], "neutral": [], "negative": []}

        # Fetch 2 comments for each sentiment
        sentiments = ["positive", "neutral", "negative"]
        comment_tasks = []
        for sentiment in sentiments:
            task = db.comments_youtube.find(
                {'source_id': {'$in': source_ids}, 'sentiment': sentiment},
                {'text': 1, 'author': 1, 'publish_date': 1, '_id': 0}
            ).sort('publish_date', -1).limit(2).to_list(length=2)

            comment_tasks.append(task)

        results = await asyncio.gather(*comment_tasks)
        # Convert datetime objects to string format for JSON response
        for sentiment_list in results:
            for comment in sentiment_list:
                if 'publish_date' in comment and hasattr(comment['publish_date'], 'isoformat'):
                    comment['publish_date'] = comment['publish_date'].isoformat()

        return dict(zip(sentiments, results))

    def fetch_interest_data():
        df = tr.interest_over_time(keywords=[main_data['keyword']], timeframe="now 7-d")

        if df.empty:
            return []

        # Resample hourly data to daily data
        daily_df = df[[main_data['keyword']]].resample('D').mean().round(0).astype(int)

        # Format for API response
        interest_data = [
            {"date": index.strftime('%Y-%m-%d'), "value": row.iloc[0]}
            for index, row in daily_df.iterrows()
        ]
        return interest_data

    # Run both task concurrently
    # comments_task = fetch_repr_comments()
    # interest_task = fetch_interest_data()
    # repr_comments, interest_data = await asyncio.gather(comments_task, interest_task)
    repr_comments = await fetch_repr_comments()
    interest_data = fetch_interest_data()

    # 3. Combine all data and return
    response_data = {
        **main_data,
        "interest_over_time": interest_data,
        "representative_comments": repr_comments
    }

    return response_data
