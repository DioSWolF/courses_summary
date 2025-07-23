from fastapi.security import APIKeyHeader
from pydantic_settings import BaseSettings
from datetime import timedelta
from app.services.rate_limiter import RateLimiter, RedisRateLimitStorage


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    Attributes:
        database_url (str): Database connection URL.
        openai_api_key (str): API key for OpenAI services.
        redis_url (str): Redis server connection URL for rate limiting and caching.
        number_of_requests (int): Maximum number of allowed requests per rate limit window (default: 3).
        limit_window_hours (int): Duration of rate limit window in hours (default: 1).
        timeout_seconds (int): Timeout duration for operations in seconds (default: 15).
        poll_interval (float): Interval in seconds for polling operations (default: 0.5).
        secret_key (str): Secret key used for JWT token encoding.
        algorithm (str): Algorithm used for JWT encoding (default: "HS256").
        access_token_expire_minutes (int): Access token expiration time in minutes (default: 60).

    Config:
        env_file (str): Path to the .env file containing environment variables.
        env_file_encoding (str): Encoding used to read the .env file.
    """

    database_url: str
    openai_api_key: str
    redis_url: str
    number_of_requests: int = 3
    limit_window_hours: int = 1
    timeout_seconds: int = 15
    poll_interval: float = 0.5
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
"""
Instance of application settings loaded from environment variables.
"""

rate_limiter = RateLimiter(
    storage=RedisRateLimitStorage(settings.redis_url),
    max_requests=settings.number_of_requests,
    window=timedelta(hours=settings.limit_window_hours),
)
"""
RateLimiter instance configured to limit requests per user using Redis storage.

Limits users to `number_of_requests` requests per `limit_window_hours`.
"""

api_key_header = APIKeyHeader(name="Authorization", auto_error=True)
"""
FastAPI security dependency to extract the `Authorization` header as an API key.

Raises an error automatically if the header is missing.
"""

"Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwiZXhwIjoxNzUzMjM3OTcxfQ.vYZKYhbFQIeP2HGIKjsJa_l88nLyJevGgLtiOUBzqNA"
