"""Caching system for LLM responses."""

import json
import hashlib
from typing import Optional, Any, Dict
from pathlib import Path
from datetime import datetime, timedelta
from ai_automation_framework.core.logger import get_logger


logger = get_logger(__name__)


class ResponseCache:
    """
    Cache for LLM responses to avoid redundant API calls.

    Implements disk-based caching with TTL (time-to-live) support.
    """

    def __init__(
        self,
        cache_dir: str = "./cache",
        ttl_hours: int = 24,
        max_size_mb: int = 100
    ):
        """
        Initialize response cache.

        Args:
            cache_dir: Directory to store cache files
            ttl_hours: Time-to-live for cache entries in hours
            max_size_mb: Maximum cache size in megabytes
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self.ttl = timedelta(hours=ttl_hours)
        self.max_size_bytes = max_size_mb * 1024 * 1024

        logger.info(f"Initialized ResponseCache at {self.cache_dir}")

    def _generate_key(
        self,
        prompt: str,
        model: str,
        temperature: float,
        **kwargs
    ) -> str:
        """Generate cache key from request parameters."""
        # Create a deterministic string from parameters
        params = {
            "prompt": prompt,
            "model": model,
            "temperature": temperature,
            **kwargs
        }

        # Sort keys for consistency
        param_str = json.dumps(params, sort_keys=True)

        # Generate hash
        return hashlib.sha256(param_str.encode()).hexdigest()

    def get(
        self,
        prompt: str,
        model: str,
        temperature: float = 0.7,
        **kwargs
    ) -> Optional[str]:
        """
        Get cached response if available and not expired.

        Args:
            prompt: Request prompt
            model: Model name
            temperature: Temperature setting
            **kwargs: Additional parameters

        Returns:
            Cached response or None
        """
        cache_key = self._generate_key(prompt, model, temperature, **kwargs)
        cache_file = self.cache_dir / f"{cache_key}.json"

        if not cache_file.exists():
            return None

        try:
            # Load cache entry
            with open(cache_file, 'r') as f:
                entry = json.load(f)

            # Check if expired
            cached_time = datetime.fromisoformat(entry['timestamp'])
            if datetime.now() - cached_time > self.ttl:
                logger.debug(f"Cache expired for key: {cache_key[:8]}...")
                cache_file.unlink()  # Remove expired entry
                return None

            logger.debug(f"Cache hit for key: {cache_key[:8]}...")
            return entry['response']

        except Exception as e:
            logger.error(f"Error reading cache: {e}")
            return None

    def set(
        self,
        prompt: str,
        response: str,
        model: str,
        temperature: float = 0.7,
        **kwargs
    ) -> None:
        """
        Cache a response.

        Args:
            prompt: Request prompt
            response: Response to cache
            model: Model name
            temperature: Temperature setting
            **kwargs: Additional parameters
        """
        cache_key = self._generate_key(prompt, model, temperature, **kwargs)
        cache_file = self.cache_dir / f"{cache_key}.json"

        entry = {
            "timestamp": datetime.now().isoformat(),
            "prompt": prompt,
            "response": response,
            "model": model,
            "temperature": temperature,
            "params": kwargs
        }

        try:
            with open(cache_file, 'w') as f:
                json.dump(entry, f, indent=2)

            logger.debug(f"Cached response for key: {cache_key[:8]}...")

            # Check cache size and cleanup if needed
            self._cleanup_if_needed()

        except Exception as e:
            logger.error(f"Error writing cache: {e}")

    def _cleanup_if_needed(self) -> None:
        """Cleanup old entries if cache size exceeds limit."""
        total_size = sum(
            f.stat().st_size
            for f in self.cache_dir.glob("*.json")
        )

        if total_size <= self.max_size_bytes:
            return

        logger.info(f"Cache size ({total_size / 1024 / 1024:.2f} MB) exceeds limit, cleaning up...")

        # Get all cache files sorted by modification time
        cache_files = sorted(
            self.cache_dir.glob("*.json"),
            key=lambda f: f.stat().st_mtime
        )

        # Remove oldest files until under limit
        current_size = total_size
        removed = 0

        for cache_file in cache_files:
            if current_size <= self.max_size_bytes:
                break

            file_size = cache_file.stat().st_size
            cache_file.unlink()
            current_size -= file_size
            removed += 1

        logger.info(f"Removed {removed} old cache entries")

    def clear(self) -> None:
        """Clear all cache entries."""
        count = 0
        for cache_file in self.cache_dir.glob("*.json"):
            cache_file.unlink()
            count += 1

        logger.info(f"Cleared {count} cache entries")

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        cache_files = list(self.cache_dir.glob("*.json"))

        total_size = sum(f.stat().st_size for f in cache_files)

        return {
            "total_entries": len(cache_files),
            "total_size_mb": total_size / 1024 / 1024,
            "cache_dir": str(self.cache_dir.absolute()),
            "ttl_hours": self.ttl.total_seconds() / 3600,
            "max_size_mb": self.max_size_bytes / 1024 / 1024
        }


# Global cache instance
_cache: Optional[ResponseCache] = None


def get_cache(
    cache_dir: str = "./cache",
    ttl_hours: int = 24
) -> ResponseCache:
    """
    Get or create global cache instance.

    Args:
        cache_dir: Cache directory
        ttl_hours: Time-to-live in hours

    Returns:
        ResponseCache instance
    """
    global _cache

    if _cache is None:
        _cache = ResponseCache(cache_dir=cache_dir, ttl_hours=ttl_hours)

    return _cache
