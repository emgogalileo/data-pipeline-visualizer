"""
Data Pipeline Visualizer — ETL Engine
======================================
A functional ETL (Extract → Transform → Load) pipeline built with Python and Pandas.

Design Principles:
  - Each stage is a pure function: (DataFrame) → DataFrame
  - Stages are composable via the Pipeline class (chain pattern)
  - All transformations are logged with execution time
  - Output can be CSV, JSON, or printed as a report

Usage:
    python pipeline.py --source data/sales_raw.csv --output results/

    python pipeline.py --demo   # runs with synthetic data
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from pathlib import Path
from typing import Callable

import pandas as pd

from stages.extract import extract_csv, generate_synthetic_data
from stages.transform import (
    drop_duplicates,
    fill_missing_values,
    normalize_column_names,
    parse_dates,
    compute_revenue,
    filter_anomalies,
    aggregate_by_period,
)
from stages.load import save_to_csv, save_to_json, print_summary

# ── Logging setup ──────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


# ── Pipeline orchestrator ──────────────────────────────────────────────────────

class Pipeline:
    """
    Chainable ETL pipeline that applies a sequence of transformation stages.

    Each stage is a callable (DataFrame) → DataFrame.
    Execution time is measured and logged per stage.

    Example:
        result = (
            Pipeline(df)
            .pipe(normalize_column_names)
            .pipe(fill_missing_values)
            .pipe(compute_revenue)
            .result()
        )
    """

    def __init__(self, df: pd.DataFrame) -> None:
        self._df = df
        self._metrics: list[dict] = []

    def pipe(self, stage: Callable[[pd.DataFrame], pd.DataFrame], **kwargs) -> "Pipeline":
        """Apply a transformation stage and record its execution time."""
        start = time.perf_counter()
        rows_before = len(self._df)

        self._df = stage(self._df, **kwargs)

        elapsed_ms = (time.perf_counter() - start) * 1000
        rows_after = len(self._df)

        self._metrics.append(
            {
                "stage": stage.__name__,
                "rows_in": rows_before,
                "rows_out": rows_after,
                "elapsed_ms": round(elapsed_ms, 2),
            }
        )
        logger.info(
            "  ✔ %-30s  %5d → %5d rows  (%6.1f ms)",
            stage.__name__,
            rows_before,
            rows_after,
            elapsed_ms,
        )
        return self

    def result(self) -> pd.DataFrame:
        """Return the transformed DataFrame."""
        return self._df

    def metrics(self) -> list[dict]:
        """Return per-stage execution metrics."""
        return self._metrics


# ── CLI entry point ────────────────────────────────────────────────────────────

def run(source_path: Path | None, output_dir: Path) -> None:
    """Execute the full ETL pipeline."""
    output_dir.mkdir(parents=True, exist_ok=True)

    # ── EXTRACT ────────────────────────────────────────────────────────────────
    logger.info("🔵  EXTRACT")
    if source_path and source_path.exists():
        raw_df = extract_csv(source_path)
    else:
        logger.info("  No source CSV provided — generating synthetic data.")
        raw_df = generate_synthetic_data(n_rows=500)

    logger.info("  Loaded %d rows, %d columns.", len(raw_df), len(raw_df.columns))

    # ── TRANSFORM ──────────────────────────────────────────────────────────────
    logger.info("🟡  TRANSFORM")
    pipeline = (
        Pipeline(raw_df)
        .pipe(normalize_column_names)
        .pipe(fill_missing_values)
        .pipe(parse_dates, column="date")
        .pipe(drop_duplicates)
        .pipe(compute_revenue)
        .pipe(filter_anomalies, column="revenue", z_threshold=3.0)
        .pipe(aggregate_by_period, period="M")
    )
    transformed_df = pipeline.result()

    # ── LOAD ───────────────────────────────────────────────────────────────────
    logger.info("🟢  LOAD")
    save_to_csv(transformed_df, output_dir / "output.csv")
    save_to_json(transformed_df, output_dir / "output.json")
    print_summary(transformed_df)

    # ── METRICS ────────────────────────────────────────────────────────────────
    metrics_path = output_dir / "pipeline_metrics.json"
    metrics_path.write_text(json.dumps(pipeline.metrics(), indent=2))
    logger.info("📊  Pipeline metrics written to %s", metrics_path)
    logger.info("✅  Pipeline complete.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Data Pipeline Visualizer — ETL Engine")
    parser.add_argument("--source", type=Path, help="Path to input CSV file", default=None)
    parser.add_argument("--output", type=Path, help="Output directory", default=Path("results"))
    parser.add_argument("--demo", action="store_true", help="Run with synthetic demo data")
    args = parser.parse_args()

    source = args.source if not args.demo else None
    run(source, args.output)


if __name__ == "__main__":
    main()
