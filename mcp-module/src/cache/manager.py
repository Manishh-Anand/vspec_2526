"""
Cache Manager
Manages MCP caching operations
"""

import asyncio
import logging
import time
from typing import Dict, Any, Optional, Union
from .backends.memory import MemoryCacheBackend
from .strategies import CacheStrategy


class CacheManager:
    """MCP Cache Manager"""
    
    def __init__(self, strategy: CacheStrategy = CacheStrategy.LRU, max_size: int = 1000, ttl: int = 3600):
        self.logger = logging.getLogger(__name__)
        self.strategy = strategy
        self.max_size = max_size
        self.ttl = ttl
        self.backend = MemoryCacheBackend(max_size, ttl)
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            return await self.backend.get(key)
        except Exception as e:
            self.logger.error(f"Error getting from cache: {e}")
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache"""
        try:
            return await self.backend.set(key, value, ttl or self.ttl)
        except Exception as e:
            self.logger.error(f"Error setting cache: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete value from cache"""
        try:
            return await self.backend.delete(key)
        except Exception as e:
            self.logger.error(f"Error deleting from cache: {e}")
            return False
    
    async def clear(self) -> bool:
        """Clear all cache"""
        try:
            return await self.backend.clear()
        except Exception as e:
            self.logger.error(f"Error clearing cache: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        try:
            return await self.backend.exists(key)
        except Exception as e:
            self.logger.error(f"Error checking cache existence: {e}")
            return False
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        try:
            return await self.backend.get_stats()
        except Exception as e:
            self.logger.error(f"Error getting cache stats: {e}")
            return {}
