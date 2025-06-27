"""Debug import issue test."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("Testing step by step imports...")

try:
    print("1. Importing cache...")
    from altman_zscore.common.cache import get_cache
    print("✅ Cache imported")
except Exception as e:
    print(f"❌ Cache import failed: {e}")
    exit(1)

try:
    print("2. Importing common modules...")
    from altman_zscore.common.logging_config import get_logger
    from altman_zscore.common.config import get_config
    from altman_zscore.common.exceptions import DataFetchError
    print("✅ Common modules imported")
except Exception as e:
    print(f"❌ Common imports failed: {e}")
    exit(1)

try:
    print("3. Importing FMP fetcher...")
    from altman_zscore.layers.data_fetch.fmp_fetcher import FMPDataFetcher
    print("✅ FMP fetcher imported")
except Exception as e:
    print(f"❌ FMP fetcher import failed: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

try:
    print("4. Importing Yahoo fetcher...")
    from altman_zscore.layers.data_fetch.yahoo_fetcher import YahooDataFetcher
    print("✅ Yahoo fetcher imported")
except Exception as e:
    print(f"❌ Yahoo fetcher import failed: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

print("✅ All imports successful!")
