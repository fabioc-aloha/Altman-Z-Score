import pandas as pd
from typing import Dict, Optional


def classify_z_score(z: Optional[float], assumptions: dict) -> Optional[str]:
    if z is None:
        return None
    if z > assumptions["safe_zone_threshold"]:
        return "Safe Zone"
    if assumptions["grey_zone_min"] <= z <= assumptions["grey_zone_max"]:
        return "Grey Zone"
    return "Distress Zone"


def build_summary_table(
    returns_df: pd.DataFrame, z_scores: dict, assumptions: dict
) -> pd.DataFrame:
    df = returns_df.copy()
    df["Z-Score"] = df["Ticker"].map(
        lambda t: z_scores[t]["z"] if t in z_scores else None
    )
    df["Diagnostic"] = df["Z-Score"].apply(lambda z: classify_z_score(z, assumptions))
    df["Missing Fields"] = df["Ticker"].map(
        lambda t: z_scores[t]["missing"] if t in z_scores else ""
    )
    df["Financials Date"] = df["Ticker"].map(
        lambda t: z_scores[t]["financials_date"] if t in z_scores else ""
    )
    df["Price as of Financials Date"] = df["Ticker"].map(
        lambda t: z_scores[t]["price_as_of_financials_date"] if t in z_scores else None
    )
    df["Staleness Warning"] = df["Ticker"].map(
        lambda t: z_scores[t]["staleness_warning"] if t in z_scores else ""
    )
    return df


def export_table(df: pd.DataFrame, filename: str, filetype: str):
    if filetype == "csv":
        df.to_csv(filename, index=False)
    elif filetype == "excel":
        df.to_excel(filename, index=False)
    else:
        raise ValueError("Unsupported filetype. Use 'csv' or 'excel'.")
