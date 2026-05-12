"""Load stage: persist transformed data to disk or display summary."""

from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)


def save_to_csv(df: pd.DataFrame, path: Path) -> None:
    """Write DataFrame to CSV (no index column)."""
    df.to_csv(path, index=False)
    logger.info("  CSV written → %s (%d rows)", path, len(df))


def save_to_json(df: pd.DataFrame, path: Path) -> None:
    """Write DataFrame to JSON (records orientation, ISO dates)."""
    df.to_json(path, orient="records", date_format="iso", indent=2)
    logger.info("  JSON written → %s", path)


def print_summary(df: pd.DataFrame) -> None:
    """Print a human-readable summary table to stdout."""
    print("\n" + "=" * 60)
    print("  PIPELINE OUTPUT SUMMARY")
    print("=" * 60)
    print(df.to_string(index=False))
    print("=" * 60 + "\n")
