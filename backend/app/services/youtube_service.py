from typing import Any, List, Dict
from app.core.config import settings
from app.core.exceptions import QuotaExceededError

from googleapiclient.discovery import build, Resource
from googleapiclient.errors import HttpError


class YouTubeService:
    """
    A service class for interacting with the YouTube Data API.
    """

    def __init__(self, api_key: str) -> None:
        self.api_key: str = api_key
        try:
            self.youtube: Resource = build("youtube", "v3", developerKey=api_key)
        except Exception as e:
            print(f"Failed to build Youtube service: {e}")
            raise

    def search_videos(
        self, query_string: str, published_after: str | None = None
    ) -> List[Dict[str, Any]]:
        """
        Searches for videos related to a keyword.
        """
        try:
            search_request = self.youtube.search().list(
                q=query_string,
                part="snippet",
                type="video",
                maxResults=settings.FETCH_VIDEOS_PER_ENTITY,
                regionCode="US",
                relevanceLanguage="en",
                publishedAfter=published_after,
                order="relevance",
            )

            response = search_request.execute()
            return response.get("items", [])

        except HttpError as e:
            # Specific error handling for quota exceeded
            content_str = e.content.decode("utf-8")
            if e.resp.status == 403 and "quotaExceeded" in content_str:
                print("YouTube API quota exceeded.")
                raise QuotaExceededError("YouTube API quota exceeded")

            print(
                f"An HTTP error {e.resp.status} occurred during video search: {e.content}"
            )
            return []
        except Exception as e:
            print(f"An unexpected error occurred during video search: {e}")
            return []

    def fetch_comments(self, video_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Fetches top-level comments for a given video ID using pagination
        until the specified limit is reached or there are no more comments.
        """
        comments: List[Dict[str, Any]] = []
        next_page_token: str | None = None

        try:
            while len(comments) < limit:
                response = (
                    self.youtube.commentThreads()
                    .list(
                        part="snippet",
                        videoId=video_id,
                        maxResults=100,
                        textFormat="plainText",
                        order="relevance",  # Fetch most relevant comments first
                        pageToken=next_page_token,
                    )
                    .execute()
                )

                for item in response.get("items", []):
                    snippet = (
                        item.get("snippet", {})
                        .get("topLevelComment", {})
                        .get("snippet", {})
                    )
                    if snippet:
                        comment_data = {
                            "comment_id": item.get("id"),
                            "text": snippet.get("textDisplay"),
                            "author": snippet.get("authorDisplayName"),
                            "publish_date": snippet.get("publishedAt"),
                        }
                        comments.append(comment_data)

                next_page_token = response.get("nextPageToken")
                if not next_page_token:
                    # No more pages of comments
                    break

        except HttpError as e:
            # Specific error handling for quota exceeded
            content_str = e.content.decode("utf-8")
            if e.resp.status == 403 and "quotaExceeded" in content_str:
                print("YouTube API quota exceeded.")
                raise QuotaExceededError("YouTube API quota has been exceeded.")

            # It's common for comments to be disabled, so we'll log it but not treat as a fatal error.
            if "commentsDisabled" in str(e.content):
                print(f"Comments are disabled for video {video_id}.")
            else:
                print(
                    f"An HTTP error {e.resp.status} occurred fetching comments: {e.content}"
                )
        except Exception as e:
            print(f"An unexpected error occurred fetching comments: {e}")

        # Always return the comments collected so far, truncated to the limit
        return comments[:limit]
