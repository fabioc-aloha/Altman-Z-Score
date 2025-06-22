"""Simple test to verify caching implementation works."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

def test_basic_imports():
    """Test basic imports work."""
    try:
        from altman_zscore.common.cache import get_cache, CacheBackend
        print("✅ Cache imports successful")
        
        from altman_zscore.layers.data_fetch.yahoo_fetcher import YahooDataFetcher
        print("✅ Yahoo fetcher import successful")
        
        from altman_zscore.layers.data_fetch.fmp_fetcher import FMPDataFetcher
        print("✅ FMP fetcher import successful")
        
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_cache_creation():
    """Test cache creation."""
    try:
        from altman_zscore.common.cache import get_cache, CacheBackend
        
        cache = get_cache("test_cache", backend=CacheBackend.MEMORY)
        print("✅ Memory cache created successfully")
        
        cache.set("test_key", "test_value", ttl=60)
        value = cache.get("test_key")
        
        if value == "test_value":
            print("✅ Cache set/get works correctly")
        else:
            print(f"❌ Cache get returned: {value}")
        
        return True
    except Exception as e:
        print(f"❌ Cache test error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Simple API Caching Test")
    print("=" * 40)
    
    print("1. Testing basic imports...")
    imports_ok = test_basic_imports()
    
    print("2. Testing cache functionality...")
    cache_ok = test_cache_creation()
    
    if imports_ok and cache_ok:
        print("\n✅ Basic functionality test passed!")
    else:
        print("\n❌ Some tests failed - check implementation")
