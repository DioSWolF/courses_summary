from abc import ABC, abstractmethod
from datetime import timedelta
from redis import Redis

from app.core.exceptions import OpenAIRateLimitError


class RateLimitStorage(ABC):
    """
    Abstract base class defining the interface for rate limit storage backends.

    Implementations must provide methods to get and increment the request count per user.
    """

    @abstractmethod
    def get_request_count(self, user_id: int) -> int:
        """
        Get the current number of requests made by the specified user within the rate limit window.

        :param user_id: int
            The user identifier.
        :return: int
            The current request count.
        """
        pass

    @abstractmethod
    def increment_request_count(self, user_id: int, window: timedelta) -> None:
        """
        Increment the request count for the specified user and set expiration for the rate limit window.

        :param user_id: int
            The user identifier.
        :param window: timedelta
            The duration of the rate limit window.
        """
        pass


class RedisRateLimitStorage(RateLimitStorage):
    """
    Redis-backed implementation of RateLimitStorage.

    Uses Redis keys with expiration to track user request counts within a time window.
    """

    def __init__(self, redis_url: str):
        """
        Initialize RedisRateLimitStorage with a Redis connection.

        :param redis_url: str
            Redis connection URL.
        """
        self.redis: Redis = Redis.from_url(redis_url, decode_responses=True)

    def get_request_count(self, user_id: int) -> int:
        """
        Get the current request count for a user from Redis.

        :param user_id: int
            The user identifier.
        :return: int
            The current request count, or 0 if no requests recorded.
        """
        count = self.redis.get(self._key(user_id))
        return int(count) if count else 0

    def increment_request_count(self, user_id: int, window: timedelta) -> None:
        """
        Increment the user's request count and set expiration to enforce the rate limit window.

        :param user_id: int
            The user identifier.
        :param window: timedelta
            The time window for rate limiting.
        """
        key = self._key(user_id)
        pipe = self.redis.pipeline()
        pipe.incr(key)
        pipe.expire(key, int(window.total_seconds()))
        pipe.execute()

    def _key(self, user_id: int) -> str:
        """
        Generate the Redis key for storing the user's request count.

        :param user_id: int
            The user identifier.
        :return: str
            The Redis key string.
        """
        return f"rate_limit:user:{user_id}"


class RateLimiter:
    """
    Rate limiter enforcing a maximum number of requests per user in a time window.

    Delegates storage of counts to a RateLimitStorage backend.
    """

    def __init__(self, storage: RateLimitStorage, max_requests: int, window: timedelta):
        """
        Initialize the RateLimiter.

        :param storage: RateLimitStorage
            Storage backend to track request counts.
        :param max_requests: int
            Maximum allowed requests within the window.
        :param window: timedelta
            Duration of the rate limit window.
        """
        self.storage = storage
        self.max_requests = max_requests
        self.window = window

    def enforce_limit(self, user_id: int):
        """
        Check and enforce the rate limit for a given user.

        Raises OpenAIRateLimitError if the user has exceeded the allowed requests.

        :param user_id: int
            The user identifier.
        :raises OpenAIRateLimitError:
            When the user exceeds the max_requests within the rate limit window.
        """
        current = self.storage.get_request_count(user_id)

        if current >= self.max_requests:
            raise OpenAIRateLimitError(
                self.max_requests, int(self.window.total_seconds() // 3600)
            )

        self.storage.increment_request_count(user_id, self.window)
