#!/usr/bin/env python3
from pathlib import Path
import duckdb

BASE = Path(__file__).resolve().parent.parent
CSV_DIR = BASE / "data_generation" / "output"
WAREHOUSE = BASE / "warehouse" / "warehouse.duckdb"

TABLES = [
    "raw_customers",
    "raw_plans",
    "raw_subscriptions",
    "raw_subscription_events",
    "raw_invoices",
    "raw_invoice_lines",
]

def main() -> None:
    CSV_DIR.mkdir(parents=True, exist_ok=True)
    WAREHOUSE.parent.mkdir(parents=True, exist_ok=True)

    conn = duckdb.connect(str(WAREHOUSE))
    conn.execute("CREATE SCHEMA IF NOT EXISTS raw")

    for table in TABLES:
        path = CSV_DIR / f"{table}.csv"
        if not path.exists():
            raise SystemExit(f"Missing CSV: {path}")
        print(f"Loading {path.name}")
        conn.execute(f"DROP TABLE IF EXISTS raw.{table}")
        conn.execute(
            f"""
            CREATE TABLE raw.{table} AS
            SELECT * FROM read_csv_auto('{path}', HEADER=TRUE)
            """
        )

    print("Done.")


if __name__ == "__main__":
    main()
