import os
from dotenv import load_dotenv, find_dotenv
from pymongo import MongoClient
from trendspy import Trends
from googleapiclient.discovery import build
from datetime import datetime as dt, timedelta

load_dotenv(find_dotenv())

MONGODB_URI = os.getenv("MONGODB_URI")
YT_API_KEY = os.getenv("YT_API_KEY")
NUM_ENTITIES = int(os.getenv("NUM_ENTITIES"))
DAYS = int(os.getenv("DAYS"))
MAX_RESULTS = int(os.getenv("MAX_RESULTS"))

if os.getenv("ENV") == "development":
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

client = MongoClient(MONGODB_URI)
dbs = client.list_database_names()
trending_db = client.trending_db

tr = Trends(language="en")
trends = tr.trending_now(geo="US", hours=24 * 7)
trends.sort(key=lambda item: item.volume, reverse=True)

youtube = build("youtube", "v3", developerKey=YT_API_KEY)


def get_rfc_time_ago(days=0, hours=0, minutes=0):
    time_ago = dt.now() - timedelta(days=days, hours=hours, minutes=minutes)
    return time_ago.strftime("%Y-%m-%dT%H:%M:%SZ")


# def search_entity_video(keyword, days=1):
#     time_ago = get_rfc_time_ago(days)

#     response = (
#         youtube.search()
#         .list(
#             q=keyword,
#             part="snippet",
#             type="video",
#             maxResults=50,
#             order="relevance",
#             # regionCode='',
#             relevanceLanguage="en",
#             publishedAfter=time_ago,
#         )
#         .execute()
#     )

#     for item in response["items"]:
#         video_id = item["id"].get("videoId")
#         title = item["snippet"]["title"]
#         print(f"{title} - https://www.youtube.com/watch?v={video_id}")

#     print(f"\n{len(response['items'])}")


def search_entity_video(keyword, days=1, max_results=50):
    time_ago = get_rfc_time_ago(days)

    all_videos = []
    next_page_token = None

    while len(all_videos) < max_results:  # dừng khi đủ 100 video
        response = (
            youtube.search()
            .list(
                q=keyword,
                part="snippet",
                type="video",
                maxResults=50,
                order="relevance",
                relevanceLanguage="en",
                publishedAfter=time_ago,
                pageToken=next_page_token,  # token phân trang
            )
            .execute()
        )

        all_videos.extend(response["items"])  # lưu kết quả

        # Nếu không còn trang tiếp theo hoặc đã đủ 100 video thì dừng
        next_page_token = response.get("nextPageToken")
        if not next_page_token:
            break

    # Giới hạn đúng 100 video
    all_videos = all_videos[:max_results]

    # In kết quả
    # for item in all_videos:
    #     video_id = item["id"].get("videoId")
    #     title = item["snippet"]["title"]
    #     print(f"{title} - https://www.youtube.com/watch?v={video_id}")

    # print(f"\nTổng số video lấy được: {len(all_videos)}")

    return all_videos


def fetch_all_comments(video_id):
    # comments = []
    author_list, comment_list, publish_list = [], [], []
    next_page = None
    try:
        while True:
            response = (
                youtube.commentThreads()
                .list(
                    part="snippet,replies",
                    videoId=video_id,
                    maxResults=100,
                    pageToken=next_page,
                    textFormat="plainText",
                )
                .execute()
            )

            for item in response.get("items", []):
                top = item["snippet"]["topLevelComment"]["snippet"]
                author_list.append(top["authorDisplayName"])
                comment_list.append(top["textDisplay"])
                publish_list.append(top["publishedAt"])
                # comments.append(
                #     {
                #         "author": top["authorDisplayName"],
                #         "text": top["textDisplay"],
                #         "likeCount": top.get("likeCount", 0),
                #         "publishedAt": top["publishedAt"],
                #     }
                # )

            next_page = response.get("nextPageToken")
            if not next_page:
                break

    except Exception as e:
        print(e)

    # return comments
    return author_list, comment_list, publish_list


def predict_sentiments(comment_list: list):
    sentiment_list = []
    for _ in comment_list:
        sentiment_list.append("neutral")

    return sentiment_list


def insert_data():
    entities_data = []
    for trend in trends[:NUM_ENTITIES]:
        entities_data.append(
            {
                "keyword": trend.keyword,
                "geo": trend.geo,
                "volume": trend.volume,
                "volume_growth_pct": trend.volume_growth_pct,
                "start_date": dt.fromtimestamp(trend.started_timestamp[0]),
                "trend_keywords": trend.trend_keywords,
            }
        )

    entities_collection = trending_db.entities
    entities = entities_collection.insert_many(entities_data).inserted_ids
    print(entities)

    videos_collection = trending_db.youtube_videos
    comments_collection = trending_db.youtube_comments

    for i in range(NUM_ENTITIES):
        all_videos = search_entity_video(
            keyword=entities_data[i]["keyword"], days=DAYS, max_results=MAX_RESULTS
        )

        videos_data = []
        num_comments = 0
        for item in all_videos:
            video_id = item["id"].get("videoId")
            if not video_id:
                continue

            snippet = item["snippet"]
            videos_data.append(
                {
                    "id": video_id,
                    "url": f"https://www.youtube.com/watch?v={video_id}",
                    "title": snippet["title"],
                    "publish_date": dt.strptime(
                        snippet["publishedAt"], "%Y-%m-%dT%H:%M:%SZ"
                    ),
                    "description": snippet["description"],
                    "thumbnail": snippet["thumbnails"]["high"]["url"],
                    "entity_id": entities[i],
                }
            )

            author_list, comment_list, publish_list = fetch_all_comments(video_id)
            if not comment_list:
                continue

            comments_data = []
            sentiment_list = predict_sentiments(comment_list)
            for j in range(len(comment_list)):
                comments_data.append(
                    {
                        "entity_id": entities[i],
                        "video_id": video_id,
                        "author": author_list[j],
                        "text": comment_list[j],
                        "publish_date": dt.strptime(
                            publish_list[j], "%Y-%m-%dT%H:%M:%SZ"
                        ),
                        "sentiment": sentiment_list[j],
                    }
                )

            comments_collection.insert_many(comments_data)
            num_comments += len(comments_data)

        # videos = videos_collection.insert_many(videos_data).inserted_ids
        videos_collection.insert_many(videos_data)
        print(f"{entities_data[i]['keyword']}: {num_comments} comment(s)")


def main():
    print(dbs)

    insert_data()


if __name__ == "__main__":
    main()
