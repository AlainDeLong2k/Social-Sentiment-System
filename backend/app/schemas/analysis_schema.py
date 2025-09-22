from typing import List, Dict
from pydantic import BaseModel, Field


# --- Schemas for Weekly Trends ---
class AnalysisResultSchema(BaseModel):
    """
    Represents the aggregated analysis counts for an entity.
    """
    total_comments: int = 0
    positive_count: int = 0
    neutral_count: int = 0
    negative_count: int = 0


class WeeklyTrendResponseSchema(BaseModel):
    """
    Represents a single trending entity in the weekly results API response.
    """
    entity_id: str = Field(..., alias='_id')
    keyword: str
    thumbnail_url: str | None = None
    analysis: AnalysisResultSchema


class WeeklyTrendListResponse(BaseModel):
    """
    Represents the top-level API response for the weekly trends endpoint.
    """
    data: List[WeeklyTrendResponseSchema]


# --- Schemas for Trend Detail ---
class InterestOverTimePoint(BaseModel):
    """
    Represents a single data point in the interest over time chart.
    """
    date: str
    value: int


class CommentSchema(BaseModel):
    """
    Represents a single representative comment.
    """
    publish_date: str
    text: str
    author: str


class RepresentativeCommentsSchema(BaseModel):
    """
    Holds lists of representative comments for each sentiment.
    """
    positive: List[CommentSchema]
    neutral: List[CommentSchema]
    negative: List[CommentSchema]


class TrendDetailResponseSchema(WeeklyTrendResponseSchema):
    """
    Represents the full detailed response for a single entity,
    inheriting basic fields from WeeklyTrendResponseSchema.
    """
    interest_over_time: List[InterestOverTimePoint]
    representative_comments: RepresentativeCommentsSchema


# --- Schemas for On-Demand Analysis ---
class OnDemandRequestSchema(BaseModel):
    """
    Defines the request body for an on-demand analysis request from a user.
    """
    keyword: str


class OnDemandResponseSchema(BaseModel):
    """
    Defines the response body after successfully queuing an on-demand job.
    """
    job_id: str
    message: str


class JobStatusResponseSchema(BaseModel):
    """
    Represents the status of an on-demand job.
    """
    job_id: str = Field(..., alias="_id")
    status: str
    keyword: str
    result: TrendDetailResponseSchema | None = None
