import hashlib
import json
import logging
import threading
import time
from collections import OrderedDict
from typing import Any

import redis

from src.config import settings

logger = logging.getLogger("cache")


class InMemoryTTLCache:
    """Thread-safe L1 In-Memory LRU Cache with TTL expiration."""

    def __init__(self, maxsize: int = 2000, default_ttl: int = 600):
        self.maxsize = maxsize
        self.default_ttl = default_ttl
        self._cache: OrderedDict[str, tuple[Any, float]] = OrderedDict()
        self._lock = threading.Lock()

    def get(self, key: str) -> Any | None:
        with self._lock:
            if key not in self._cache:
                return None
            val, expire_at = self._cache[key]
            if time.time() > expire_at:
                del self._cache[key]
                return None
            self._cache.move_to_end(key)
            return val

    def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        ttl = ttl if ttl is not None else self.default_ttl
        expire_at = time.time() + ttl
        with self._lock:
            if key in self._cache:
                self._cache.move_to_end(key)
            self._cache[key] = (value, expire_at)
            if len(self._cache) > self.maxsize:
                self._cache.popitem(last=False)

    def delete(self, key: str) -> None:
        with self._lock:
            self._cache.pop(key, None)

    def delete_prefix(self, prefix: str) -> int:
        with self._lock:
            keys_to_del = [k for k in self._cache if k.startswith(prefix)]
            for k in keys_to_del:
                del self._cache[k]
            return len(keys_to_del)

    def clear(self) -> None:
        with self._lock:
            self._cache.clear()

    def __len__(self) -> int:
        with self._lock:
            return len(self._cache)


class MultiTierCache:
    """
    Two-Tier Caching System:
    - Tier 1 (L1): In-Memory LRU Cache (< 0.1ms latency)
    - Tier 2 (L2): Redis Distributed Cache (~ 1-2ms latency) with in-memory fallback
    """

    def __init__(self, redis_url: str | None = None):
        self.l1 = InMemoryTTLCache(
            maxsize=3000, default_ttl=settings.search_cache_ttl_seconds
        )
        self.redis_url = redis_url or settings.redis_url
        self._redis_client: redis.Redis | None = None
        self._redis_available: bool = False
        self._in_memory_l2 = InMemoryTTLCache(
            maxsize=10000, default_ttl=settings.exact_cache_ttl_seconds
        )

        # Telemetry metrics
        self.l1_hits: int = 0
        self.l2_hits: int = 0
        self.misses: int = 0
        self._metrics_lock = threading.Lock()

        self._connect_redis()

    def _connect_redis(self) -> None:
        try:
            client = redis.Redis.from_url(
                self.redis_url,
                socket_timeout=1.5,
                socket_connect_timeout=1.5,
                decode_responses=True,
            )
            client.ping()
            self._redis_client = client
            self._redis_available = True
            logger.info("Connected to Redis successfully.")
        except Exception as e:
            logger.warning(f"Redis unavailable, operating with in-memory L2 cache: {e}")
            self._redis_client = None
            self._redis_available = False

    @staticmethod
    def generate_key(prefix: str, payload: Any) -> str:
        """Generates deterministic SHA-256 cache key from payload dictionary or string."""
        if isinstance(payload, dict):
            serialized = json.dumps(payload, sort_keys=True, default=str)
        else:
            serialized = str(payload).strip().lower()
        hash_digest = hashlib.sha256(serialized.encode("utf-8")).hexdigest()[:16]
        return f"{prefix}:{hash_digest}"

    def get(self, key: str) -> Any | None:
        # 1. Check L1 Memory Cache
        val = self.l1.get(key)
        if val is not None:
            with self._metrics_lock:
                self.l1_hits += 1
            return val

        # 2. Check L2 Cache (Redis or In-Memory fallback)
        if self._redis_available and self._redis_client:
            try:
                raw_data = self._redis_client.get(key)
                if raw_data:
                    val = json.loads(raw_data)
                    # Populate L1 for future instant access
                    self.l1.set(
                        key, val, ttl=min(60, settings.search_cache_ttl_seconds)
                    )
                    with self._metrics_lock:
                        self.l2_hits += 1
                    return val
            except Exception as e:
                logger.warning(f"Redis get failed: {e}")

        # Check fallback L2
        fallback_val = self._in_memory_l2.get(key)
        if fallback_val is not None:
            self.l1.set(
                key, fallback_val, ttl=min(60, settings.search_cache_ttl_seconds)
            )
            with self._metrics_lock:
                self.l2_hits += 1
            return fallback_val

        with self._metrics_lock:
            self.misses += 1
        return None

    def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        ttl = ttl if ttl is not None else settings.search_cache_ttl_seconds
        # Write to L1
        self.l1.set(key, value, ttl=ttl)

        # Write to L2 (Redis or fallback)
        serialized = json.dumps(value, default=str)
        if self._redis_available and self._redis_client:
            try:
                self._redis_client.set(key, serialized, ex=ttl)
                return
            except Exception as e:
                logger.warning(f"Redis set failed: {e}")

        self._in_memory_l2.set(key, value, ttl=ttl)

    def delete(self, key: str) -> None:
        self.l1.delete(key)
        if self._redis_available and self._redis_client:
            try:
                self._redis_client.delete(key)
            except Exception:
                pass
        self._in_memory_l2.delete(key)

    def invalidate_prefix(self, prefix: str) -> int:
        """Evicts all cache keys matching a prefix (e.g. 'search:', 'prod:')."""
        count = self.l1.delete_prefix(prefix)
        count += self._in_memory_l2.delete_prefix(prefix)
        if self._redis_available and self._redis_client:
            try:
                keys = self._redis_client.keys(f"{prefix}*")
                if keys:
                    self._redis_client.delete(*keys)
            except Exception:
                pass
        return count

    def get_stats(self) -> dict[str, Any]:
        with self._metrics_lock:
            total_requests = self.l1_hits + self.l2_hits + self.misses
            hit_count = self.l1_hits + self.l2_hits
            hit_ratio = (
                round((hit_count / total_requests) * 100, 2)
                if total_requests > 0
                else 0.0
            )
            return {
                "total_cache_requests": total_requests,
                "l1_hits": self.l1_hits,
                "l2_hits": self.l2_hits,
                "misses": self.misses,
                "overall_hit_ratio_pct": hit_ratio,
                "redis_connected": self._redis_available,
                "l1_keys_cached": len(self.l1),
            }

    def clear(self) -> None:
        self.l1.clear()
        if self._redis_available and self._redis_client:
            try:
                self._redis_client.flushdb()
            except Exception:
                pass
        self._in_memory_l2.clear()


global_cache = MultiTierCache()
