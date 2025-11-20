"""
Utility script that turns the cleaned CSV into a SQLite database that Datasette
can serve. Run this after updating the CSV to refresh military_slots.db.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Optional

import pandas as pd
import sqlite_utils

BASE_DIR = Path(__file__).parent
CSV_PATH = BASE_DIR / "data" / "District_Revenue_FY20-FY24_with_lat_lon_clean.csv"
DB_PATH = BASE_DIR / "military_slots.db"
TABLE_NAME = "slot_machine_revenue"

MONTH_LOOKUP: Dict[str, int] = {
    "january": 1,
    "february": 2,
    "march": 3,
    "april": 4,
    "may": 5,
    "june": 6,
    "july": 7,
    "august": 8,
    "september": 9,
    "october": 10,
    "november": 11,
    "december": 12,
}


def month_to_number(month_name: str) -> Optional[int]:
    if isinstance(month_name, str):
        return MONTH_LOOKUP.get(month_name.strip().lower())
    return None


def month_to_fiscal_year(calendar_year: Optional[int], month_number: Optional[int]) -> Optional[int]:
    if calendar_year is None or month_number is None:
        return None
    return int(calendar_year) + (1 if month_number >= 10 else 0)


def main() -> None:
    if not CSV_PATH.exists():
        raise FileNotFoundError(f"CSV not found at {CSV_PATH}")

    df = pd.read_csv(CSV_PATH)

    df["month_name"] = df["Month"].astype(str).str.strip().str.title()
    df["month_number"] = df["month_name"].str.lower().map(MONTH_LOOKUP)
    df["calendar_year"] = pd.to_numeric(df["Year"], errors="coerce").astype("Int64")
    df["revenue"] = pd.to_numeric(df["Amount"], errors="coerce").astype(float)
    df["fiscal_year"] = df.apply(
        lambda row: month_to_fiscal_year(row["calendar_year"], row["month_number"]), axis=1
    ).astype("Int64")

    df["installation_name"] = df["Base"].astype(str).str.strip()
    df["facility_name"] = df["Location"].astype(str).str.strip()
    df["branch"] = df["Service"].astype(str).str.strip()
    df["district"] = df["Region"].astype(str).str.strip()
    df["category"] = df["Category"].astype(str).str.strip()
    df["latitude"] = pd.to_numeric(df["Base_lat"], errors="coerce")
    df["longitude"] = pd.to_numeric(df["Base_lon"], errors="coerce")
    column_order = [
        "installation_name",
        "facility_name",
        "branch",
        "district",
        "category",
        "calendar_year",
        "fiscal_year",
        "month_name",
        "month_number",
        "revenue",
        "latitude",
        "longitude",
    ]

    missing = [col for col in column_order if col not in df.columns]
    if missing:
        raise ValueError(f"Missing expected columns: {missing}")

    # Replace pandas NA with plain None so sqlite-utils can persist them.
    df = df.where(pd.notnull(df), None)

    db = sqlite_utils.Database(DB_PATH)
    if TABLE_NAME in db.table_names():
        db[TABLE_NAME].drop()

    records = df[column_order].to_dict(orient="records")
    schema_sql = f"""
    CREATE TABLE [{TABLE_NAME}] (
        installation_name TEXT,
        facility_name TEXT,
        branch TEXT,
        district TEXT,
        category TEXT,
        calendar_year INTEGER,
        fiscal_year INTEGER,
        month_name TEXT,
        month_number INTEGER,
        revenue REAL,
        latitude REAL,
        longitude REAL
    )
    """
    db.execute(schema_sql)

    db[TABLE_NAME].insert_all(
        records,
        column_order=column_order,
        batch_size=500,
    )

    table = db[TABLE_NAME]
    for col in ("branch", "district", "fiscal_year", "installation_name"):
        table.create_index([col], if_not_exists=True)

    print(f"Wrote {len(records)} records to {DB_PATH}")


if __name__ == "__main__":
    main()
