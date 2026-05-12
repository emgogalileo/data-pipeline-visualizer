"""
Transform stage: pure functions that clean, enrich, and aggregate data.

Rules:
  - Every function accepts a DataFrame and returns a DataFrame.
  - No global state; all parameters are explicit arguments.
  - Functions are individually unit-testable.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def normalize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """Strip whitespace and lowercase all column names."""
    df = df.copy()
    df.columns = df.columns.str.strip().str.lower().str.replace(r"\s+", "_", regex=True)
    return df


def fill_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    Fill missing numeric columns with column median;
    fill missing string columns with 'unknown'.
    """
    df = df.copy()
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            df[col] = df[col].fillna(df[col].median())
        else:
            df[col] = df[col].fillna("unknown")
    return df


def parse_dates(df: pd.DataFrame, column: str = "date") -> pd.DataFrame:
    """Parse a string column to datetime and extract year/month/day features."""
    df = df.copy()
    if column in df.columns:
        df[column] = pd.to_datetime(df[column], errors="coerce")
        df["year"] = df[column].dt.year
        df["month"] = df[column].dt.month
        df["day"] = df[column].dt.day
    return df


def drop_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """Remove exact duplicate rows."""
    return df.drop_duplicates().reset_index(drop=True)


def compute_revenue(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add a 'revenue' column as quantity × unit_price.
    Requires both columns to exist after normalization.
    """
    df = df.copy()
    if "quantity" in df.columns and "unit_price" in df.columns:
        df["revenue"] = df["quantity"] * df["unit_price"]
    return df


def filter_anomalies(df: pd.DataFrame, column: str = "revenue", z_threshold: float = 3.0) -> pd.DataFrame:
    """
    Remove rows where the specified column's Z-score exceeds the threshold.
    Standard statistical outlier removal (|Z| > 3 → ~0.3% of normal data).
    """
    df = df.copy()
    if column not in df.columns:
        return df
    mean = df[column].mean()
    std = df[column].std()
    if std == 0:
        return df
    z_scores = (df[column] - mean) / std
    return df[z_scores.abs() <= z_threshold].reset_index(drop=True)


def aggregate_by_period(df: pd.DataFrame, period: str = "M") -> pd.DataFrame:
    """
    Aggregate numeric columns by calendar period (default: monthly).

    Args:
        df:     Input DataFrame (must have a 'date' column).
        period: Pandas offset alias — 'D' (daily), 'W' (weekly), 'M' (monthly).

    Returns:
        Aggregated DataFrame with total revenue, quantity, and transaction count.
    """
    df = df.copy()
    if "date" not in df.columns:
        return df
    df["period"] = df["date"].dt.to_period(period).astype(str)

    agg = (
        df.groupby("period")
        .agg(
            total_revenue=("revenue", "sum"),
            total_quantity=("quantity", "sum"),
            transactions=("revenue", "count"),
            avg_order_value=("revenue", "mean"),
        )
        .reset_index()
    )
    agg["total_revenue"] = agg["total_revenue"].round(2)
    agg["avg_order_value"] = agg["avg_order_value"].round(2)
    return agg
