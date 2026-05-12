# Data Pipeline Visualizer

A production-grade ETL pipeline written in **Python** using Pandas.  
Extracts raw sales data, applies a series of transformations, and loads clean aggregated results.

## Tech Stack
- **Language**: Python 3.11+
- **Data**: Pandas 2.2, NumPy 1.26
- **Pattern**: Chainable Pipeline (each stage is a pure function)

## Getting Started

```bash
# Install dependencies
pip install -r requirements.txt

# Run with synthetic demo data
python pipeline.py --demo

# Run with your own CSV
python pipeline.py --source path/to/sales.csv --output results/
```

## Pipeline Stages

```
[EXTRACT]
  └─ extract_csv / generate_synthetic_data

[TRANSFORM]
  ├─ normalize_column_names   → lowercase + snake_case
  ├─ fill_missing_values      → median (numeric) / 'unknown' (string)
  ├─ parse_dates              → datetime + year/month/day features
  ├─ drop_duplicates          → exact row deduplication
  ├─ compute_revenue          → quantity × unit_price
  ├─ filter_anomalies         → Z-score outlier removal (|Z| > 3)
  └─ aggregate_by_period      → monthly groupby summary

[LOAD]
  ├─ save_to_csv     → results/output.csv
  ├─ save_to_json    → results/output.json
  └─ print_summary   → console table
```

## Output

| File | Description |
|------|-------------|
| `results/output.csv` | Aggregated monthly data |
| `results/output.json` | Same data in JSON records format |
| `results/pipeline_metrics.json` | Stage-by-stage execution times |

## Project Structure

```
pipeline.py         # Orchestrator + CLI
stages/
├── extract.py      # Data ingestion
├── transform.py    # Pure transformation functions
└── load.py         # Output writers
```

## Author
Emmanuel García — [emmanuelg@allcognition.com](mailto:emmanuelg@allcognition.com)
