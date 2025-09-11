"""
Memory Cache Backend
In-memory cache implementation
"""

import asyncio
import logging
import time
from typing import Dict, Any, Optional, Union
from collections import OrderedDict


class MemoryCacheBackend:
    """In-memory cache backend"""
    
    def __init__(self, max_size: int = 1000, ttl: int = 3600):
        self.max_size = max_size
        self.ttl = ttl
        self.logger = logging.getLogger(__name__)
        self.cache: OrderedDict = OrderedDict()
        self.timestamps: Dict[str, float] = {}
        self.stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'deletes': 0
        }
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            # Check if key exists and is not expired
            if key in self.cache:
                if self._is_expired(key):
                    await self.delete(key)
                    self.stats['misses'] += 1
                    return None
                
                # Move to end (LRU)
                value = self.cache.pop(key)
                self.cache[key] = value
                self.stats['hits'] += 1
                return value
            
            self.stats['misses'] += 1
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting from memory cache: {e}")
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache"""
        try:
            # Remove if exists
            if key in self.cache:
                del self.cache[key]
            
            # Check size limit
            if len(self.cache) >= self.max_size:
                # Remove oldest item
                oldest_key = next(iter(self.cache))
                del self.cache[oldest_key]
                del self.timestamps[oldest_key]
            
            # Add new item
            self.cache[key] = value
            self.timestamps[key] = time.time()
            self.stats['sets'] += 1
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error setting memory cache: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete value from cache"""
        try:
            if key in self.cache:
                del self.cache[key]
                del self.timestamps[key]
                self.stats['deletes'] += 1
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error deleting from memory cache: {e}")
            return False
    
    async def clear(self) -> bool:
        """Clear all cache"""
        try:
            self.cache.clear()
            self.timestamps.clear()
            return True
        except Exception as e:
            self.logger.error(f"Error clearing memory cache: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        try:
            if key in self.cache:
                if self._is_expired(key):
                    await self.delete(key)
                    return False
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error checking memory cache existence: {e}")
            return False
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        try:
            # Clean expired items
            await self._cleanup_expired()
            
            total_requests = self.stats['hits'] + self.stats['misses']
            hit_rate = self.stats['hits'] / total_requests if total_requests > 0 else 0
            
            return {
                'size': len(self.cache),
                'max_size': self.max_size,
                'hits': self.stats['hits'],
                'misses': self.stats['misses'],
                'sets': self.stats['sets'],
                'deletes': self.stats['deletes'],
                'hit_rate': hit_rate,
                'ttl': self.ttl
            }
        except Exception as e:
            self.logger.error(f"Error getting memory cache stats: {e}")
            return {}
    
    def _is_expired(self, key: str) -> bool:
        """Check if key is expired"""
        if key not in self.timestamps:
            return True
        
        return time.time() - self.timestamps[key] > self.ttl
    
    async def _cleanup_expired(self) -> None:
        """Clean up expired items"""
        try:
            expired_keys = []
            for key in self.cache:
                if self._is_expired(key):
                    expired_keys.append(key)
            
            for key in expired_keys:
                await self.delete(key)
                
        except Exception as e:
            self.logger.error(f"Error cleaning up expired items: {e}")
