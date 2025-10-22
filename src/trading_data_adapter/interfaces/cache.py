"""Cache repository interface."""
from abc import ABC, abstractmethod
from typing import Any, List, Optional


class CacheRepository(ABC):
    """Repository interface for caching operations."""

    @abstractmethod
    async def get(self, key: str) -> Optional[str]:
        """Get a value from cache."""
        pass

    @abstractmethod
    async def set(self, key: str, value: str, ttl: Optional[int] = None) -> None:
        """Set a value in cache with optional TTL (seconds)."""
        pass

    @abstractmethod
    async def delete(self, key: str) -> None:
        """Delete a value from cache."""
        pass

    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        pass

    @abstractmethod
    async def get_json(self, key: str) -> Optional[Any]:
        """Get and deserialize JSON value from cache."""
        pass

    @abstractmethod
    async def set_json(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Serialize and set JSON value in cache."""
        pass

    @abstractmethod
    async def get_many(self, keys: List[str]) -> List[Optional[str]]:
        """Get multiple values from cache."""
        pass

    @abstractmethod
    async def set_many(self, items: dict[str, str], ttl: Optional[int] = None) -> None:
        """Set multiple values in cache."""
        pass

    @abstractmethod
    async def delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern, return count deleted."""
        pass

    @abstractmethod
    async def keys(self, pattern: str) -> List[str]:
        """Get all keys matching pattern."""
        pass

    @abstractmethod
    async def ttl(self, key: str) -> int:
        """Get time-to-live for a key in seconds (-1 if no TTL, -2 if not exists)."""
        pass

    @abstractmethod
    async def expire(self, key: str, ttl: int) -> None:
        """Set expiration time for a key."""
        pass

    @abstractmethod
    async def increment(self, key: str, amount: int = 1) -> int:
        """Increment a numeric value, return new value."""
        pass

    @abstractmethod
    async def decrement(self, key: str, amount: int = 1) -> int:
        """Decrement a numeric value, return new value."""
        pass
