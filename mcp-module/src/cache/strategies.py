"""
Cache Strategies
Different caching strategies for MCP
"""

from enum import Enum
from typing import Dict, Any, List


class CacheStrategy(Enum):
    """Cache strategies"""
    LRU = "lru"  # Least Recently Used
    LFU = "lfu"  # Least Frequently Used
    FIFO = "fifo"  # First In First Out
    TTL = "ttl"  # Time To Live


class CacheStrategyFactory:
    """Factory for creating cache strategies"""
    
    @staticmethod
    def create_strategy(strategy: CacheStrategy, **kwargs) -> 'BaseCacheStrategy':
        """Create a cache strategy instance"""
        if strategy == CacheStrategy.LRU:
            return LRUStrategy(**kwargs)
        elif strategy == CacheStrategy.LFU:
            return LFUStrategy(**kwargs)
        elif strategy == CacheStrategy.FIFO:
            return FIFOStrategy(**kwargs)
        elif strategy == CacheStrategy.TTL:
            return TTLStrategy(**kwargs)
        else:
            raise ValueError(f"Unknown cache strategy: {strategy}")


class BaseCacheStrategy:
    """Base cache strategy"""
    
    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
    
    def should_evict(self, cache: Dict[str, Any]) -> bool:
        """Check if cache should evict items"""
        return len(cache) >= self.max_size
    
    def select_eviction_candidate(self, cache: Dict[str, Any]) -> str:
        """Select item to evict"""
        raise NotImplementedError
    
    def update_access(self, key: str, cache: Dict[str, Any]) -> None:
        """Update access information"""
        pass


class LRUStrategy(BaseCacheStrategy):
    """Least Recently Used strategy"""
    
    def __init__(self, max_size: int = 1000):
        super().__init__(max_size)
        self.access_order: List[str] = []
    
    def select_eviction_candidate(self, cache: Dict[str, Any]) -> str:
        """Select least recently used item"""
        if self.access_order:
            return self.access_order[0]
        return next(iter(cache.keys()))
    
    def update_access(self, key: str, cache: Dict[str, Any]) -> None:
        """Update access order"""
        if key in self.access_order:
            self.access_order.remove(key)
        self.access_order.append(key)
        
        # Remove if not in cache
        if key not in cache:
            self.access_order.remove(key)


class LFUStrategy(BaseCacheStrategy):
    """Least Frequently Used strategy"""
    
    def __init__(self, max_size: int = 1000):
        super().__init__(max_size)
        self.access_counts: Dict[str, int] = {}
    
    def select_eviction_candidate(self, cache: Dict[str, Any]) -> str:
        """Select least frequently used item"""
        if not self.access_counts:
            return next(iter(cache.keys()))
        
        min_count = min(self.access_counts.values())
        candidates = [k for k, v in self.access_counts.items() if v == min_count]
        return candidates[0]
    
    def update_access(self, key: str, cache: Dict[str, Any]) -> None:
        """Update access count"""
        self.access_counts[key] = self.access_counts.get(key, 0) + 1
        
        # Remove if not in cache
        if key not in cache:
            del self.access_counts[key]


class FIFOStrategy(BaseCacheStrategy):
    """First In First Out strategy"""
    
    def __init__(self, max_size: int = 1000):
        super().__init__(max_size)
        self.insertion_order: List[str] = []
    
    def select_eviction_candidate(self, cache: Dict[str, Any]) -> str:
        """Select first inserted item"""
        if self.insertion_order:
            return self.insertion_order[0]
        return next(iter(cache.keys()))
    
    def update_access(self, key: str, cache: Dict[str, Any]) -> None:
        """Update insertion order"""
        if key not in self.insertion_order and key in cache:
            self.insertion_order.append(key)
        
        # Remove if not in cache
        if key not in cache and key in self.insertion_order:
            self.insertion_order.remove(key)


class TTLStrategy(BaseCacheStrategy):
    """Time To Live strategy"""
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 3600):
        super().__init__(max_size)
        self.default_ttl = default_ttl
        self.expiry_times: Dict[str, float] = {}
    
    def select_eviction_candidate(self, cache: Dict[str, Any]) -> str:
        """Select expired item or oldest item"""
        import time
        current_time = time.time()
        
        # Find expired items
        expired = [k for k, v in self.expiry_times.items() if v < current_time]
        if expired:
            return expired[0]
        
        # Find oldest item
        if self.expiry_times:
            oldest_key = min(self.expiry_times.keys(), key=lambda k: self.expiry_times[k])
            return oldest_key
        
        return next(iter(cache.keys()))
    
    def update_access(self, key: str, cache: Dict[str, Any]) -> None:
        """Update expiry time"""
        import time
        if key in cache:
            self.expiry_times[key] = time.time() + self.default_ttl
        
        # Remove if not in cache
        if key not in cache and key in self.expiry_times:
            del self.expiry_times[key]
