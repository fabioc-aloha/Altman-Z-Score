"""
Unified caching framework for the Altman Z-Score pipeline.

This module provides a unified caching interface for all layers with TTL-based
cache management, cache invalidation strategies, and support for different backends.
"""

import os
import json
import pickle
import hashlib
import threading
import time
from abc import ABC, abstractmethod
from typing import Any, Optional, Dict, List, Union, Callable, TypeVar, Generic
from dataclasses import dataclass
from pathlib import Path
from enum import Enum

from .logging_config import get_logger
from .exceptions import AltmanZScoreError
from .utils import ensure_dir_exists

logger = get_logger(__name__)

T = TypeVar('T')


class CacheBackend(Enum):
    """Cache backend types."""
    MEMORY = "memory"
    FILE = "file"
    HYBRID = "hybrid"


@dataclass
class CacheEntry:
    """Cache entry with metadata."""
    key: str
    value: Any
    created_at: float
    accessed_at: float
    ttl: Optional[float] = None  # Time to live in seconds
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
    
    @property
    def is_expired(self) -> bool:
        """Check if cache entry is expired."""
        if self.ttl is None:
            return False
        return time.time() - self.created_at > self.ttl
    
    @property
    def age(self) -> float:
        """Get age of cache entry in seconds."""
        return time.time() - self.created_at
    
    def touch(self) -> None:
        """Update access time."""
        self.accessed_at = time.time()


class CacheBackendInterface(ABC, Generic[T]):
    """Abstract interface for cache backends."""
    
    @abstractmethod
    def get(self, key: str) -> Optional[CacheEntry]:
        """Get cache entry by key."""
        pass
    
    @abstractmethod
    def set(self, key: str, value: T, ttl: Optional[float] = None, 
            metadata: Optional[Dict[str, Any]] = None) -> None:
        """Set cache entry."""
        pass
    
    @abstractmethod
    def delete(self, key: str) -> bool:
        """Delete cache entry."""
        pass
    
    @abstractmethod
    def clear(self) -> None:
        """Clear all cache entries."""
        pass
    
    @abstractmethod
    def keys(self) -> List[str]:
        """Get all cache keys."""
        pass
    
    @abstractmethod
    def cleanup_expired(self) -> int:
        """Remove expired entries and return count."""
        pass


class MemoryCacheBackend(CacheBackendInterface[T]):
    """In-memory cache backend with thread safety."""
    
    def __init__(self, max_size: Optional[int] = None):
        """
        Initialize memory cache backend.
        
        Args:
            max_size: Maximum number of entries (None for unlimited)
        """
        self._cache: Dict[str, CacheEntry] = {}
        self._lock = threading.RLock()
        self._max_size = max_size
    
    def get(self, key: str) -> Optional[CacheEntry]:
        """Get cache entry by key."""
        with self._lock:
            entry = self._cache.get(key)
            if entry is None:
                return None
            
            if entry.is_expired:
                del self._cache[key]
                return None
            
            entry.touch()
            return entry
    
    def set(self, key: str, value: T, ttl: Optional[float] = None,
            metadata: Optional[Dict[str, Any]] = None) -> None:
        """Set cache entry."""
        with self._lock:
            # Evict oldest entries if at max size
            if self._max_size and len(self._cache) >= self._max_size:
                if key not in self._cache:  # Only evict if this is a new key
                    self._evict_lru()
            
            now = time.time()
            entry = CacheEntry(
                key=key,
                value=value,
                created_at=now,
                accessed_at=now,
                ttl=ttl,
                metadata=metadata or {}
            )
            
            self._cache[key] = entry
    
    def delete(self, key: str) -> bool:
        """Delete cache entry."""
        with self._lock:
            return self._cache.pop(key, None) is not None
    
    def clear(self) -> None:
        """Clear all cache entries."""
        with self._lock:
            self._cache.clear()
    
    def keys(self) -> List[str]:
        """Get all cache keys."""
        with self._lock:
            return list(self._cache.keys())
    
    def cleanup_expired(self) -> int:
        """Remove expired entries and return count."""
        with self._lock:
            expired_keys = []
            for key, entry in self._cache.items():
                if entry.is_expired:
                    expired_keys.append(key)
            
            for key in expired_keys:
                del self._cache[key]
            
            return len(expired_keys)
    
    def _evict_lru(self) -> None:
        """Evict least recently used entry."""
        if not self._cache:
            return
        
        lru_key = min(self._cache.keys(), 
                     key=lambda k: self._cache[k].accessed_at)
        del self._cache[lru_key]


class FileCacheBackend(CacheBackendInterface[T]):
    """File-based cache backend with JSON/pickle serialization."""
    
    def __init__(self, cache_dir: Union[str, Path], 
                 serializer: str = "json",
                 max_size_mb: Optional[float] = None):
        """
        Initialize file cache backend.
        
        Args:
            cache_dir: Directory to store cache files
            serializer: "json" or "pickle"
            max_size_mb: Maximum cache size in MB (None for unlimited)
        """
        self.cache_dir = Path(cache_dir)
        self.serializer = serializer
        self.max_size_mb = max_size_mb
        self._lock = threading.RLock()
          # Ensure cache directory exists
        ensure_dir_exists(str(self.cache_dir))
        
        # Validate serializer
        if serializer not in ["json", "pickle"]:
            raise AltmanZScoreError(f"Unsupported serializer: {serializer}")
    
    def _get_cache_path(self, key: str) -> Path:
        """Get file path for cache key."""
        # Hash the key to avoid filesystem issues
        key_hash = hashlib.sha256(key.encode()).hexdigest()
        extension = ".json" if self.serializer == "json" else ".pkl"
        return self.cache_dir / f"{key_hash}{extension}"
    
    def _serialize(self, value: Any) -> bytes:
        """Serialize value to bytes."""
        if self.serializer == "json":
            return json.dumps(value, default=str).encode('utf-8')
        else:  # pickle
            return pickle.dumps(value)
    
    def _deserialize(self, data: bytes) -> Any:
        """Deserialize bytes to value."""
        if self.serializer == "json":
            return json.loads(data.decode('utf-8'))
        else:  # pickle
            return pickle.loads(data)
    
    def get(self, key: str) -> Optional[CacheEntry]:
        """Get cache entry by key."""
        cache_path = self._get_cache_path(key)
        
        with self._lock:
            if not cache_path.exists():
                return None
            
            try:
                # Read metadata and check expiration
                metadata_path = cache_path.with_suffix(cache_path.suffix + '.meta')
                if metadata_path.exists():
                    with open(metadata_path, 'r') as f:
                        meta = json.load(f)
                    
                    entry = CacheEntry(
                        key=key,
                        value=None,  # Will be loaded below
                        created_at=meta['created_at'],
                        accessed_at=meta['accessed_at'],
                        ttl=meta.get('ttl'),
                        metadata=meta.get('metadata', {})
                    )
                    
                    if entry.is_expired:
                        cache_path.unlink(missing_ok=True)
                        metadata_path.unlink(missing_ok=True)
                        return None
                
                # Load value
                with open(cache_path, 'rb') as f:
                    data = f.read()
                    value = self._deserialize(data)
                
                if metadata_path.exists():
                    entry.value = value
                    entry.touch()
                    
                    # Update access time in metadata
                    meta['accessed_at'] = entry.accessed_at
                    with open(metadata_path, 'w') as f:
                        json.dump(meta, f)
                    
                    return entry
                else:
                    # Legacy entry without metadata
                    now = time.time()
                    return CacheEntry(
                        key=key,
                        value=value,
                        created_at=cache_path.stat().st_mtime,
                        accessed_at=now,
                        ttl=None,
                        metadata={}
                    )
                
            except Exception as e:
                logger.warning(f"Failed to load cache entry '{key}': {e}")
                cache_path.unlink(missing_ok=True)
                return None
    
    def set(self, key: str, value: T, ttl: Optional[float] = None,
            metadata: Optional[Dict[str, Any]] = None) -> None:
        """Set cache entry."""
        cache_path = self._get_cache_path(key)
        metadata_path = cache_path.with_suffix(cache_path.suffix + '.meta')
        
        with self._lock:
            try:
                # Check cache size limit
                if self.max_size_mb:
                    self._enforce_size_limit()
                
                # Serialize and write value
                data = self._serialize(value)
                with open(cache_path, 'wb') as f:
                    f.write(data)
                
                # Write metadata
                now = time.time()
                meta = {
                    'key': key,
                    'created_at': now,
                    'accessed_at': now,
                    'ttl': ttl,
                    'metadata': metadata or {}
                }
                
                with open(metadata_path, 'w') as f:
                    json.dump(meta, f, indent=2)
                
            except Exception as e:
                logger.error(f"Failed to cache entry '{key}': {e}")
                cache_path.unlink(missing_ok=True)
                metadata_path.unlink(missing_ok=True)
                raise AltmanZScoreError(f"Cache write failed: {e}")
    
    def delete(self, key: str) -> bool:
        """Delete cache entry."""
        cache_path = self._get_cache_path(key)
        metadata_path = cache_path.with_suffix(cache_path.suffix + '.meta')
        
        with self._lock:
            deleted = False
            if cache_path.exists():
                cache_path.unlink()
                deleted = True
            
            if metadata_path.exists():
                metadata_path.unlink()
            
            return deleted
    
    def clear(self) -> None:
        """Clear all cache entries."""
        with self._lock:
            for file_path in self.cache_dir.glob("*"):
                if file_path.is_file():
                    file_path.unlink()
    
    def keys(self) -> List[str]:
        """Get all cache keys."""
        keys = []
        with self._lock:
            for meta_path in self.cache_dir.glob("*.meta"):
                try:
                    with open(meta_path, 'r') as f:
                        meta = json.load(f)
                        keys.append(meta['key'])
                except Exception:
                    continue
        
        return keys
    
    def cleanup_expired(self) -> int:
        """Remove expired entries and return count."""
        with self._lock:
            expired_count = 0
            for meta_path in self.cache_dir.glob("*.meta"):
                try:
                    with open(meta_path, 'r') as f:
                        meta = json.load(f)
                    
                    if meta.get('ttl'):
                        created_at = meta['created_at']
                        ttl = meta['ttl']
                        if time.time() - created_at > ttl:
                            # Remove both metadata and cache files
                            cache_path = meta_path.with_suffix('')
                            meta_path.unlink(missing_ok=True)
                            cache_path.unlink(missing_ok=True)
                            expired_count += 1
                
                except Exception:
                    continue
            
            return expired_count
    
    def _enforce_size_limit(self) -> None:
        """Enforce cache size limit by removing oldest entries."""
        if not self.max_size_mb:
            return
        
        total_size = sum(f.stat().st_size for f in self.cache_dir.glob("*") 
                        if f.is_file()) / (1024 * 1024)  # Convert to MB
        
        if total_size <= self.max_size_mb:
            return
        
        # Get all cache files with their access times
        files_with_time = []
        for meta_path in self.cache_dir.glob("*.meta"):
            try:
                with open(meta_path, 'r') as f:
                    meta = json.load(f)
                cache_path = meta_path.with_suffix('')
                files_with_time.append((meta['accessed_at'], meta_path, cache_path))
            except Exception:
                continue
        
        # Sort by access time (oldest first)
        files_with_time.sort(key=lambda x: x[0])
        
        # Remove oldest entries until under size limit
        for _, meta_path, cache_path in files_with_time:
            meta_path.unlink(missing_ok=True)
            cache_path.unlink(missing_ok=True)
            
            total_size = sum(f.stat().st_size for f in self.cache_dir.glob("*") 
                           if f.is_file()) / (1024 * 1024)
            
            if total_size <= self.max_size_mb:
                break


class UnifiedCache:
    """
    Unified cache interface supporting multiple backends and layers.
    
    Features:
    - Multiple backend support (memory, file, hybrid)
    - Automatic TTL management
    - Cache invalidation strategies
    - Statistics and monitoring
    - Thread-safe operations
    """
    
    def __init__(self, 
                 backend: CacheBackend = CacheBackend.MEMORY,
                 cache_dir: Optional[Union[str, Path]] = None,
                 ttl_seconds: Optional[float] = None,
                 max_memory_entries: Optional[int] = 1000,
                 max_file_size_mb: Optional[float] = 100.0,
                 cleanup_interval: float = 300.0,  # 5 minutes
                 serializer: str = "json"):  # Default serializer
        """
        Initialize unified cache.
        
        Args:
            backend: Cache backend type
            cache_dir: Directory for file cache (required for FILE/HYBRID)
            ttl_seconds: Default TTL for cache entries
            max_memory_entries: Maximum entries in memory cache
            max_file_size_mb: Maximum file cache size in MB
            cleanup_interval: Seconds between automatic cleanup
            serializer: Serialization format for file cache ("json" or "pickle")
        """
        self.backend_type = backend
        self.default_ttl = ttl_seconds
        self._stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'deletes': 0,
            'cleanups': 0
        }
        self._lock = threading.RLock()
        
        # Initialize backend(s)
        if backend == CacheBackend.MEMORY:
            self._primary = MemoryCacheBackend(max_size=max_memory_entries)
            self._secondary = None
        
        elif backend == CacheBackend.FILE:
            if cache_dir is None:
                raise AltmanZScoreError("cache_dir required for FILE backend")
            self._primary = FileCacheBackend(cache_dir, serializer=serializer, max_size_mb=max_file_size_mb)
            self._secondary = None
        
        elif backend == CacheBackend.HYBRID:
            if cache_dir is None:
                raise AltmanZScoreError("cache_dir required for HYBRID backend")
            self._primary = MemoryCacheBackend(max_size=max_memory_entries)
            self._secondary = FileCacheBackend(cache_dir, serializer=serializer, max_size_mb=max_file_size_mb)
        
        else:
            raise AltmanZScoreError(f"Unsupported backend: {backend}")
        
        # Start cleanup timer
        if cleanup_interval > 0:
            self._start_cleanup_timer(cleanup_interval)
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get value from cache.
        
        Args:
            key: Cache key
            default: Default value if key not found
            
        Returns:
            Cached value or default
        """
        with self._lock:
            # Try primary cache first
            entry = self._primary.get(key)
            if entry is not None:
                self._stats['hits'] += 1
                return entry.value
            
            # Try secondary cache (if hybrid)
            if self._secondary:
                entry = self._secondary.get(key)
                if entry is not None:
                    # Promote to primary cache
                    self._primary.set(key, entry.value, entry.ttl, entry.metadata)
                    self._stats['hits'] += 1
                    return entry.value
            
            self._stats['misses'] += 1
            return default
    
    def set(self, key: str, value: Any, ttl: Optional[float] = None,
            metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (uses default if None)
            metadata: Optional metadata
        """
        with self._lock:
            ttl = ttl or self.default_ttl
            
            # Set in primary cache
            self._primary.set(key, value, ttl, metadata)
            
            # Set in secondary cache (if hybrid)
            if self._secondary:
                self._secondary.set(key, value, ttl, metadata)
            
            self._stats['sets'] += 1
    
    def delete(self, key: str) -> bool:
        """
        Delete key from cache.
        
        Args:
            key: Cache key
            
        Returns:
            True if key was deleted
        """
        with self._lock:
            deleted = self._primary.delete(key)
            
            if self._secondary:
                deleted = self._secondary.delete(key) or deleted
            
            if deleted:
                self._stats['deletes'] += 1
            
            return deleted
    
    def clear(self) -> None:
        """Clear all cache entries."""
        with self._lock:
            self._primary.clear()
            if self._secondary:
                self._secondary.clear()
            
            # Reset stats except configuration
            self._stats.update({
                'hits': 0,
                'misses': 0,
                'sets': 0,
                'deletes': 0
            })
    
    def keys(self) -> List[str]:
        """Get all cache keys."""
        with self._lock:
            keys = set(self._primary.keys())
            if self._secondary:
                keys.update(self._secondary.keys())
            return list(keys)
    
    def invalidate_pattern(self, pattern: str) -> int:
        """
        Invalidate keys matching pattern.
        
        Args:
            pattern: Key pattern (supports * wildcards)
            
        Returns:
            Number of keys invalidated
        """
        import fnmatch
        
        with self._lock:
            keys_to_delete = []
            for key in self.keys():
                if fnmatch.fnmatch(key, pattern):
                    keys_to_delete.append(key)
            
            for key in keys_to_delete:
                self.delete(key)
            
            return len(keys_to_delete)
    
    def cleanup_expired(self) -> int:
        """Remove expired entries and return count."""
        with self._lock:
            expired_count = self._primary.cleanup_expired()
            
            if self._secondary:
                expired_count += self._secondary.cleanup_expired()
            
            self._stats['cleanups'] += 1
            return expired_count
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self._lock:
            stats = self._stats.copy()
            stats['total_requests'] = stats['hits'] + stats['misses']
            stats['hit_rate'] = (stats['hits'] / stats['total_requests'] 
                               if stats['total_requests'] > 0 else 0.0)
            stats['key_count'] = len(self.keys())
            return stats
    
    def _start_cleanup_timer(self, interval: float) -> None:
        """Start automatic cleanup timer."""
        def cleanup_loop():
            while True:
                time.sleep(interval)
                try:
                    expired = self.cleanup_expired()
                    if expired > 0:
                        logger.debug(f"Cleaned up {expired} expired cache entries")
                except Exception as e:
                    logger.warning(f"Cache cleanup error: {e}")
        
        cleanup_thread = threading.Thread(target=cleanup_loop, daemon=True)
        cleanup_thread.start()


# Decorator for method caching
def cached(cache: UnifiedCache, ttl: Optional[float] = None,
          key_prefix: str = "", include_args: bool = True):
    """
    Decorator for caching function results.
    
    Args:
        cache: UnifiedCache instance
        ttl: Cache TTL in seconds
        key_prefix: Prefix for cache keys
        include_args: Whether to include function arguments in cache key
    """
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            # Generate cache key
            if include_args:
                key_parts = [func.__name__]
                if key_prefix:
                    key_parts.insert(0, key_prefix)
                
                # Add args to key
                for arg in args:
                    key_parts.append(str(hash(str(arg)))[:8])
                
                # Add kwargs to key
                for k, v in sorted(kwargs.items()):
                    key_parts.append(f"{k}={hash(str(v))}".encode().hex()[:8])
                
                cache_key = ":".join(key_parts)
            else:
                cache_key = f"{key_prefix}:{func.__name__}" if key_prefix else func.__name__
            
            # Try to get from cache
            result = cache.get(cache_key)
            if result is not None:
                return result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl)
            return result
        
        return wrapper
    return decorator


# Global cache instances
_global_caches: Dict[str, UnifiedCache] = {}
_cache_lock = threading.RLock()


def get_cache(name: str = "default", 
              backend: CacheBackend = CacheBackend.MEMORY,
              **kwargs) -> UnifiedCache:
    """
    Get or create a named cache instance.
    
    Args:
        name: Cache name
        backend: Cache backend type
        **kwargs: Additional arguments for cache initialization
        
    Returns:
        UnifiedCache instance
    """
    with _cache_lock:
        if name not in _global_caches:
            _global_caches[name] = UnifiedCache(backend=backend, **kwargs)
        return _global_caches[name]
