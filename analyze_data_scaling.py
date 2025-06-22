#!/usr/bin/env python3
"""
Data Scaling Analysis - Check the units and scaling of FMP vs Yahoo data
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from altman_zscore.layers.data_fetch.data_merger import DataMerger


async def main():
    print("Analyzing data scaling for MSFT...")
    
    data_merger = DataMerger()
    merged_data = await data_merger.merge_financial_data("MSFT")
    
    print("\n=== FMP Financial Data (raw_fmp_data) ===")
    if merged_data.raw_fmp_data:
        for key, value in merged_data.raw_fmp_data.items():
            if isinstance(value, (int, float)) and value != 0:
                print(f"{key}: {value:,.0f}")
    
    print("\n=== Yahoo Market Data ===")
    print(f"Market Cap: ${merged_data.market_cap:,.0f}" if merged_data.market_cap else "Market Cap: N/A")
    print(f"Shares Outstanding: {merged_data.shares_outstanding:,.0f}" if merged_data.shares_outstanding else "Shares Outstanding: N/A")
    print(f"Current Price: ${merged_data.current_price:.2f}" if merged_data.current_price else "Current Price: N/A")
    
    print("\n=== Calculated Ratios ===")
    print(f"Working Capital Ratio: {merged_data.working_capital_ratio:.4f}" if merged_data.working_capital_ratio else "Working Capital Ratio: N/A")
    print(f"EBIT Ratio: {merged_data.ebit_ratio:.4f}" if merged_data.ebit_ratio else "EBIT Ratio: N/A")
    print(f"Asset Turnover: {merged_data.asset_turnover:.4f}" if merged_data.asset_turnover else "Asset Turnover: N/A")
    
    print("\n=== Scale Analysis ===")
    if merged_data.raw_fmp_data and merged_data.market_cap:
        total_assets = merged_data.raw_fmp_data.get('total_assets', 0)
        market_cap = merged_data.market_cap
        
        if total_assets > 0:
            ratio = market_cap / total_assets
            print(f"Market Cap / Total Assets = {ratio:,.2f}")
            print(f"This suggests market cap scaling issue if ratio > 100")
            
            # Calculate what the market cap should be in the same units as total assets
            if ratio > 1000:  # Likely market cap is in dollars, assets in thousands
                suggested_market_cap = market_cap / 1000
                print(f"Suggested market cap scaling: ${suggested_market_cap:,.0f}K (divide by 1,000)")
            elif ratio > 1000000:  # Market cap in dollars, assets in millions
                suggested_market_cap = market_cap / 1000000
                print(f"Suggested market cap scaling: ${suggested_market_cap:,.0f}M (divide by 1,000,000)")


if __name__ == "__main__":
    asyncio.run(main())
