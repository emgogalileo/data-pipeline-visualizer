"""Extract stage: read data from files or generate synthetic datasets."""

from __future__ import annotations

import random
from pathlib import Path

import pandas as pd


def extract_csv(path: Path) -> pd.DataFrame:
    """
    Read a CSV file into a DataFrame.

    Args:
        path: Absolute or relative path to the CSV file.

    Returns:
        Raw DataFrame with all original columns.
    """
    return pd.read_csv(path, low_memory=False)


def generate_synthetic_data(n_rows: int = 500) -> pd.DataFrame:
    """
    Generate a synthetic sales dataset for pipeline demonstration.

    Schema:
        Date, Product, Category, Quantity, Unit_Price, Region, Customer_ID

    Args:
        n_rows: Number of rows to generate.

    Returns:
        DataFrame with realistic sales data (some nulls and duplicates included).
    """
    random.seed(42)

    products = ["Widget A", "Widget B", "Gadget X", "Gadget Y", "Service Z"]
    categories = ["Hardware", "Software", "Services"]
    regions = ["North", "South", "East", "West", "Central"]

    dates = pd.date_range(start="2024-01-01", periods=n_rows, freq="h")

    data = {
        "Date": [str(d.date()) for d in dates],
        "Product": [random.choice(products) for _ in range(n_rows)],
        "Category": [random.choice(categories) for _ in range(n_rows)],
        "Quantity": [random.randint(1, 100) if random.random() > 0.05 else None for _ in range(n_rows)],
        "Unit_Price": [round(random.uniform(9.99, 499.99), 2) if random.random() > 0.03 else None for _ in range(n_rows)],
        "Region": [random.choice(regions) for _ in range(n_rows)],
        "Customer_ID": [f"C{random.randint(1000, 9999)}" for _ in range(n_rows)],
    }

    df = pd.DataFrame(data)

    # Inject ~2% duplicates to test dedup stage
    dupes = df.sample(frac=0.02, random_state=1)
    return pd.concat([df, dupes], ignore_index=True)
