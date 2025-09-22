from pydantic_settings import BaseSettings, SettingsConfigDict
from urllib.parse import quote_plus


class Settings(BaseSettings):
    """
    Manages application settings and loads environment variables from a .env file.
    It constructs the complete MongoDB connection string from individual components.
    """

    # Database name
    DB_NAME: str

    # AI Model name
    SENTIMENT_MODEL: str

    # YouTube API Key
    YT_API_KEY: str

    # MongoDB connection details
    MONGODB_URI: str
    MONGODB_USR: str
    MONGODB_PWD: str

    # Kafka Name Topic
    KAFKA_TOPIC: str

    # Data Fetching Strategy Settings
    FETCH_NUM_ENTITIES: int = 20
    FETCH_VIDEOS_PER_ENTITY: int = 5
    FETCH_COMMENTS_PER_VIDEO: int = 100
    FETCH_TOTAL_COMMENTS_PER_ENTITY: int = 500
    FETCH_TRENDS_GEO: str = "US"
    FETCH_TRENDS_WITHIN_DAYS: int = 7

    # Consumer Performance Settings
    CONSUMER_BATCH_SIZE: int = 32
    CONSUMER_BATCH_TIMEOUT_SECONDS: int = 5

    # FastAPI
    API_PREFIX: str = "/api"
    API_VERSION: str = "/v1"
    API_PREFIX_TRENDS: str
    DEBUG: bool = False

    # QStash Settings
    QSTASH_URL: str = "https://qstash.upstash.io"
    QSTASH_TOKEN: str
    QSTASH_CURRENT_SIGNING_KEY: str
    QSTASH_NEXT_SIGNING_KEY: str

    # Base URL for the application, used for constructing callback URLs
    BASE_URL: str = "http://localhost:8000"

    # On-Demand Use Case
    ON_DEMAND_COMMENTS_PER_VIDEO: int = 100
    ON_DEMAND_TOTAL_COMMENTS: int = 500

    # Pydantic model configuration to load from .env file
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    @property
    def MONGODB_CONNECTION_STRING(self) -> str:
        """
        Constructs and returns the full MongoDB connection string,
        properly escaping the username and password.
        """
        # Escape username and password to handle special characters
        escaped_usr = quote_plus(self.MONGODB_USR)
        escaped_pwd = quote_plus(self.MONGODB_PWD)

        # Replace placeholders in the URI
        return self.MONGODB_URI.replace("<username>", escaped_usr).replace(
            "<password>", escaped_pwd
        )


# Create a single instance of the Settings class
settings = Settings()
