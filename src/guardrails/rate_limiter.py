import threading
import time

import redis

from src.config import settings
from src.search.cache import global_cache


class SlidingWindowRateLimiter:
    """
    Sliding window rate limiter for LLM API and client requests.
    Enforces OpenRouter free tier constraints:
    - 20 Requests Per Minute (RPM)
    - 1,000 Requests Per Day (RPD)
    """

    def __init__(
        self,
        max_rpm: int = 20,
        max_rpd: int = 1000,
        redis_client: redis.Redis | None = None,
    ):
        self.max_rpm = max_rpm
        self.max_rpd = max_rpd
        self._redis = redis_client or (
            global_cache._redis_client if global_cache._redis_available else None
        )

        # In-memory fallback
        self._minute_window: list[float] = []
        self._day_window: list[float] = []
        self._client_windows: dict[str, list[float]] = {}
        self._lock = threading.Lock()

    def acquire_llm_slot(self) -> tuple[bool, float, int]:
        """
        Attempts to acquire a slot for calling LLM API.
        Returns: (allowed, wait_seconds_if_blocked, current_rpm)
        """
        now = time.time()

        # Redis sliding window using sorted sets
        if self._redis:
            try:
                pipe = self._redis.pipeline()
                minute_key = "ratelimit:llm:rpm"
                day_key = "ratelimit:llm:rpd"

                # Clear timestamps older than 60s
                pipe.zremrangebyscore(minute_key, 0, now - 60)
                # Clear timestamps older than 86400s
                pipe.zremrangebyscore(day_key, 0, now - 86400)
                # Count remaining
                pipe.zcard(minute_key)
                pipe.zcard(day_key)
                res = pipe.execute()

                current_rpm = res[2]
                current_rpd = res[3]

                if current_rpm >= self.max_rpm:
                    # Get oldest timestamp in current minute window to compute wait time
                    oldest = self._redis.zrange(minute_key, 0, 0, withscores=True)
                    wait_sec = max(0.1, (oldest[0][1] + 60) - now) if oldest else 1.0
                    return False, round(wait_sec, 2), current_rpm

                if current_rpd >= self.max_rpd:
                    return False, 3600.0, current_rpm

                # Add current request
                pipe = self._redis.pipeline()
                pipe.zadd(minute_key, {str(now): now})
                pipe.expire(minute_key, 70)
                pipe.zadd(day_key, {str(now): now})
                pipe.expire(day_key, 86500)
                pipe.execute()

                return True, 0.0, current_rpm + 1
            except Exception:
                pass

        # In-memory sliding window fallback
        with self._lock:
            # Clean minute window
            self._minute_window = [ts for ts in self._minute_window if now - ts < 60.0]
            # Clean day window
            self._day_window = [ts for ts in self._day_window if now - ts < 86400.0]

            current_rpm = len(self._minute_window)
            current_rpd = len(self._day_window)

            if current_rpm >= self.max_rpm:
                oldest = self._minute_window[0] if self._minute_window else now
                wait_sec = max(0.1, (oldest + 60.0) - now)
                return False, round(wait_sec, 2), current_rpm

            if current_rpd >= self.max_rpd:
                return False, 3600.0, current_rpm

            self._minute_window.append(now)
            self._day_window.append(now)
            return True, 0.0, current_rpm + 1

    def acquire_client_slot(
        self, client_id: str, limit_rpm: int = 60
    ) -> tuple[bool, float]:
        """Per-client IP rate limiter."""
        now = time.time()
        with self._lock:
            window = self._client_windows.get(client_id, [])
            window = [ts for ts in window if now - ts < 60.0]
            if len(window) >= limit_rpm:
                oldest = window[0]
                wait_sec = max(0.1, (oldest + 60.0) - now)
                self._client_windows[client_id] = window
                return False, round(wait_sec, 2)
            window.append(now)
            self._client_windows[client_id] = window
            return True, 0.0


llm_rate_limiter = SlidingWindowRateLimiter(
    max_rpm=settings.llm_rpm_limit, max_rpd=settings.llm_rpd_limit
)
