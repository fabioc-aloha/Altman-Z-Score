"""
Merges quarterly financial data from SEC and Yahoo sources, preferring SEC but filling gaps with Yahoo.
"""
from typing import List, Dict

def merge_quarters_by_period(sec_quarters: List[Dict], yahoo_quarters: List[Dict], prefer_sec: bool = True) -> List[Dict]:
    """
    Merge two lists of quarterly financials (dicts with 'period_end' keys), preferring SEC for each field but using Yahoo as fallback.
    Args:
        sec_quarters: List of SEC quarterly dicts.
        yahoo_quarters: List of Yahoo quarterly dicts.
        prefer_sec: If True, SEC is primary; else Yahoo is primary.
    Returns:
        List of merged quarterly dicts.
    """
    # Index by period_end for fast lookup
    sec_map = {q["period_end"]: q for q in sec_quarters if "period_end" in q}
    yahoo_map = {q["period_end"]: q for q in yahoo_quarters if "period_end" in q}
    all_periods = sorted(set(sec_map) | set(yahoo_map))
    merged = []
    for period in all_periods:
        merged_q = {}
        sec_q = sec_map.get(period, {})
        yahoo_q = yahoo_map.get(period, {})
        # Use all keys from both sources
        all_keys = set(sec_q) | set(yahoo_q)
        for k in all_keys:
            if prefer_sec:
                merged_q[k] = sec_q.get(k, yahoo_q.get(k))
            else:
                merged_q[k] = yahoo_q.get(k, sec_q.get(k))
        merged_q["_source"] = "SEC" if period in sec_map else "Yahoo"
        merged.append(merged_q)
    return merged
