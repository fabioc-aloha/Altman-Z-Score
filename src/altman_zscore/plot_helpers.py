"""
Helper functions for preparing price statistics for plotting in Altman Z-Score visualizations.
"""

import pandas as pd


def align_dates_to_grid(date_series, freq="W"):
    """
    Align dates to weekly or monthly grid to ensure consistent mapping.
    """
    dates = pd.to_datetime(date_series)
    if freq == "W":
        # Align to Monday
        return dates - pd.Timedelta(days=dates.dt.weekday)
    else:
        # Align to first of month
        return dates.dt.to_period("M").dt.to_timestamp("M")


def prepare_price_stats_for_plotting(price_stats, using_weekly, date_to_pos, min_date, max_date):
    """
    Normalize, filter, map, and sort price stats for plotting.
    Returns: (period_positions, avg_prices, min_prices, max_prices) as lists, or (None, None, None, None) if no valid data.
    """
    if price_stats is None or price_stats.empty:
        return None, None, None, None
    price_stats = price_stats.copy()
    if using_weekly:
        price_stats["period"] = align_dates_to_grid(price_stats["week"], "W")
    else:
        price_stats["period"] = align_dates_to_grid(price_stats["month"], "M")
    mask = (price_stats["period"] >= min_date) & (price_stats["period"] <= max_date)
    price_stats = price_stats[mask].copy()
    period_positions = []
    for period in price_stats["period"]:
        pos = date_to_pos.get(period, -1)
        period_positions.append(pos)
    valid_indices = [i for i, pos in enumerate(period_positions) if pos != -1]
    if not valid_indices:
        return None, None, None, None
    period_positions = [period_positions[i] for i in valid_indices]
    avg_prices = [float(price_stats.iloc[i]["avg_price"]) for i in valid_indices]
    min_prices = [float(price_stats.iloc[i]["min_price"]) for i in valid_indices]
    max_prices = [float(price_stats.iloc[i]["max_price"]) for i in valid_indices]
    data = list(zip(period_positions, avg_prices, min_prices, max_prices))
    data.sort(key=lambda x: x[0])
    period_positions, avg_prices, min_prices, max_prices = zip(*data)
    return list(period_positions), list(avg_prices), list(min_prices), list(max_prices)


def prepare_weekly_price_stats_for_plotting(price_stats, date_to_pos, min_date, max_date):
    """
    Prepare weekly-grain price stats for plotting.
    Returns: (period_positions, avg_prices, min_prices, max_prices) as lists, or (None, None, None, None) if no valid data.
    """
    if price_stats is None or price_stats.empty:
        print("[DEBUG] Empty price stats")
        return None, None, None, None

    try:
        price_stats = price_stats.copy()
        # Ensure dates are datetime
        min_date = pd.to_datetime(min_date)
        max_date = pd.to_datetime(max_date)

        # Convert week column and align to Mondays
        price_stats["period"] = pd.to_datetime(price_stats["week"])
        # Align to Monday of each week
        price_stats["period"] = price_stats["period"].apply(lambda x: x - pd.Timedelta(days=x.weekday()))

        # Filter to date range
        mask = (price_stats["period"] >= min_date) & (price_stats["period"] <= max_date)
        price_stats = price_stats[mask].copy()

        if price_stats.empty:
            print("[DEBUG] No data after date filtering")
            return None, None, None, None

        # Get positions while handling missing values
        period_positions = []
        valid_values = []

        for period in price_stats["period"]:
            try:
                pos = date_to_pos.get(period, -1)
                if pos != -1:
                    period_positions.append(pos)
                    row = price_stats[price_stats["period"] == period].iloc[0]
                    valid_values.append(
                        {
                            "avg": float(row["avg_price"]),
                            "min": float(row["min_price"]),
                            "max": float(row["max_price"]),
                        }
                    )
                else:
                    print(f"[DEBUG] No position found for date {period}")
            except (ValueError, TypeError, KeyError) as e:
                print(f"[DEBUG] Error processing row: {e}")

        if not valid_values:
            return None, None, None, None

        # Sort by position
        sorted_data = sorted(zip(period_positions, valid_values), key=lambda x: x[0])
        period_positions = [x[0] for x in sorted_data]
        avg_prices = [x[1]["avg"] for x in sorted_data]
        min_prices = [x[1]["min"] for x in sorted_data]
        max_prices = [x[1]["max"] for x in sorted_data]

        return period_positions, avg_prices, min_prices, max_prices

    except (ValueError, TypeError):
        return None, None, None, None


def prepare_monthly_price_stats_for_plotting(price_stats, date_to_pos, min_date, max_date):
    """
    Prepare monthly-grain price stats for plotting.
    Returns: (period_positions, avg_prices, min_prices, max_prices) as lists, or (None, None, None, None) if no valid data.
    """
    if price_stats is None or price_stats.empty:
        print("[DEBUG] Empty price stats")
        return None, None, None, None

    try:
        # Convert input dates to pandas Timestamp
        min_date = pd.to_datetime(min_date)
        max_date = pd.to_datetime(max_date)

        # Create a working copy and ensure dates are datetime
        price_stats = price_stats.copy()
        price_stats["month"] = pd.to_datetime(price_stats["month"])

        # Set the period to the first of each month
        price_stats["period"] = price_stats["month"].dt.to_period("M").dt.to_timestamp()

        # Debug output
        print(f"[DEBUG] Date range: {min_date} to {max_date}")
        print(f"[DEBUG] Price stats periods: {price_stats['period'].min()} to {price_stats['period'].max()}")

        # Filter to date range
        mask = (price_stats["period"] >= min_date) & (price_stats["period"] <= max_date)
        price_stats = price_stats[mask].copy()

        if price_stats.empty:
            print("[DEBUG] No data after date filtering")
            return None, None, None, None

        # Get positions while handling missing values
        period_positions = []
        valid_values = []

        for period in price_stats["period"]:
            try:
                pos = date_to_pos.get(period, -1)
                if pos != -1:
                    period_positions.append(pos)
                    row = price_stats[price_stats["period"] == period].iloc[0]
                    valid_values.append(
                        {
                            "avg": float(row["avg_price"]),
                            "min": float(row["min_price"]),
                            "max": float(row["max_price"]),
                        }
                    )
                else:
                    print(f"[DEBUG] No position found for date {period}")
            except (ValueError, TypeError, KeyError) as e:
                print(f"[DEBUG] Error processing row: {e}")

        if not valid_values:
            return None, None, None, None

        # Sort by position
        sorted_data = sorted(zip(period_positions, valid_values), key=lambda x: x[0])
        period_positions = [x[0] for x in sorted_data]
        avg_prices = [x[1]["avg"] for x in sorted_data]
        min_prices = [x[1]["min"] for x in sorted_data]
        max_prices = [x[1]["max"] for x in sorted_data]

        return period_positions, avg_prices, min_prices, max_prices

    except (ValueError, TypeError):
        return None, None, None, None
