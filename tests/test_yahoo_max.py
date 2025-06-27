#!/usr/bin/env python3
"""
Test the updated Yahoo fetcher to verify it gets all available data by default.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from altman_zscore.layers.data_fetch.yahoo_fetcher import YahooDataFetcher

def test_yahoo_fetcher():
    print("Testing Yahoo fetcher with max data...")
    
    fetcher = YahooDataFetcher()
    
    # Test default behavior (should now be "max")
    print("1. Testing default behavior (should fetch 'max' period)...")
    history = fetcher.get_historical_prices("AAPL")
    
    if history is not None:
        print(f"   Success! Retrieved {len(history)} records")
        print(f"   Type: {type(history)}")
        print(f"   Columns: {list(history.columns) if hasattr(history, 'columns') else 'No columns attr'}")
        print(f"   Index: {type(history.index) if hasattr(history, 'index') else 'No index attr'}")
        if hasattr(history, 'index'):
            print(f"   Date range: {history.index.min()} to {history.index.max()}")
            print(f"   Span: {(history.index.max() - history.index.min()).days} days")
    else:
        print("   Failed to retrieve data")
    
    # Test explicit max period
    print("2. Testing explicit 'max' period...")
    history_max = fetcher.get_historical_prices("AAPL", period="max")
    
    if history_max is not None:
        print(f"   Success! Retrieved {len(history_max)} records")
        print(f"   Date range: {history_max['Date'].min() if 'Date' in history_max.columns else history_max.index.min()} to {history_max['Date'].max() if 'Date' in history_max.columns else history_max.index.max()}")
        date_range = (history_max['Date'].max() if 'Date' in history_max.columns else history_max.index.max()) - (history_max['Date'].min() if 'Date' in history_max.columns else history_max.index.min())
        print(f"   Span: {date_range.days} days")
    else:
        print("   Failed to retrieve data")
    
    # Test new get_all_historical_prices method
    print("3. Testing get_all_historical_prices method...")
    history_all = fetcher.get_all_historical_prices("AAPL")
    
    if history_all is not None:
        print(f"   Success! Retrieved {len(history_all)} records")
        print(f"   Date range: {history_all['Date'].min() if 'Date' in history_all.columns else history_all.index.min()} to {history_all['Date'].max() if 'Date' in history_all.columns else history_all.index.max()}")
        date_range = (history_all['Date'].max() if 'Date' in history_all.columns else history_all.index.max()) - (history_all['Date'].min() if 'Date' in history_all.columns else history_all.index.min())
        print(f"   Span: {date_range.days} days")
    else:
        print("   Failed to retrieve data")
    
    # Verify they're the same
    if history is not None and history_max is not None:
        print(f"4. Comparing default vs explicit max: Same length? {len(history) == len(history_max)}")
    
    print("Test completed!")

if __name__ == "__main__":
    test_yahoo_fetcher()
