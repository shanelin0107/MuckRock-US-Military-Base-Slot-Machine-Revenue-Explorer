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
MARINE_CSV_PATH = BASE_DIR / "data" / "Marine_Revenue_FY20-FY24_detail_with_gps.csv"
NAVY_SUMMARY_CSV_PATH = BASE_DIR / "data" / "Navy_Revenue_Reimburse_Summary_updated.csv"
NAVY_MONTHLY_CSV_PATH = BASE_DIR / "data" / "Navy Revenue Report FY20-FY24-2_monthly_summary.csv"
DB_PATH = BASE_DIR / "military_slots.db"
TABLE_NAME = "slot_machine_revenue"
MARINE_TABLE = "marine_revenue_detail"
NAVY_SUMMARY_TABLE = "navy_revenue_summary"
NAVY_MONTHLY_TABLE = "navy_revenue_monthly_summary"

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
    if not MARINE_CSV_PATH.exists():
        raise FileNotFoundError(f"Marine CSV not found at {MARINE_CSV_PATH}")
    if not NAVY_SUMMARY_CSV_PATH.exists():
        raise FileNotFoundError(f"Navy summary CSV not found at {NAVY_SUMMARY_CSV_PATH}")
    if not NAVY_MONTHLY_CSV_PATH.exists():
        raise FileNotFoundError(f"Navy monthly CSV not found at {NAVY_MONTHLY_CSV_PATH}")

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
    df["base_latitude"] = pd.to_numeric(df["Base_lat"], errors="coerce")
    df["base_longitude"] = pd.to_numeric(df["Base_lon"], errors="coerce")
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
        "base_latitude",
        "base_longitude",
    ]

    missing = [col for col in column_order if col not in df.columns]
    if missing:
        raise ValueError(f"Missing expected columns: {missing}")

    # Replace pandas NA with plain None so sqlite-utils can persist them.
    df = df.where(pd.notnull(df), None)

    db = sqlite_utils.Database(DB_PATH)
    if TABLE_NAME in db.table_names():
        db[TABLE_NAME].drop()
    if MARINE_TABLE in db.table_names():
        db[MARINE_TABLE].drop()
    if NAVY_SUMMARY_TABLE in db.table_names():
        db[NAVY_SUMMARY_TABLE].drop()
    if NAVY_MONTHLY_TABLE in db.table_names():
        db[NAVY_MONTHLY_TABLE].drop()

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
        base_latitude REAL,
        base_longitude REAL
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

    # Load Marine Corps detail CSV into its own table.
    marine_df = pd.read_csv(MARINE_CSV_PATH)
    marine_df.columns = [c.strip() for c in marine_df.columns]
    marine_df = marine_df.rename(
        columns={
            "Page": "page",
            "Loc #": "loc_id",
            "Base": "base_name",
            "Location": "location_name",
            "Month": "month_label",
            "Revenue": "revenue",
            "NAFI Amount": "nafi_amount",
            "Annual Revenue": "annual_revenue",
            "Annual NAFI": "annual_nafi",
            "Latitude": "base_latitude",
            "Longitude": "base_longitude",
            "\tLatitude": "base_latitude",
        }
    )
    marine_df["revenue"] = pd.to_numeric(marine_df["revenue"], errors="coerce")
    marine_df["nafi_amount"] = pd.to_numeric(marine_df["nafi_amount"], errors="coerce")
    marine_df["annual_revenue"] = pd.to_numeric(marine_df["annual_revenue"], errors="coerce")
    marine_df["annual_nafi"] = pd.to_numeric(marine_df["annual_nafi"], errors="coerce")
    marine_df["base_latitude"] = pd.to_numeric(marine_df["base_latitude"], errors="coerce")
    marine_df["base_longitude"] = pd.to_numeric(marine_df["base_longitude"], errors="coerce")
    marine_df["loc_id"] = pd.to_numeric(marine_df["loc_id"], errors="coerce").astype("Int64")
    marine_df["page"] = pd.to_numeric(marine_df["page"], errors="coerce").astype("Int64")

    marine_df = marine_df.where(pd.notnull(marine_df), None)

    marine_columns = [
        "page",
        "loc_id",
        "base_name",
        "location_name",
        "month_label",
        "revenue",
        "nafi_amount",
        "annual_revenue",
        "annual_nafi",
        "base_latitude",
        "base_longitude",
    ]
    marine_records = marine_df[marine_columns].to_dict(orient="records")
    db[MARINE_TABLE].insert_all(
        marine_records,
        column_order=marine_columns,
        batch_size=500,
        replace=True,
    )
    marine_table = db[MARINE_TABLE]
    for col in ("BASE_NAME", "LOCATION_NAME", "MONTH_LABEL"):
        marine_table.create_index([col], if_not_exists=True)

    print(f"Wrote {len(records)} records to {DB_PATH}")
    print(f"Wrote {len(marine_records)} marine detail records to {DB_PATH}")

    # Load Navy revenue summary CSV.
    navy_summary_df = pd.read_csv(NAVY_SUMMARY_CSV_PATH)
    navy_summary_df.columns = [c.strip() for c in navy_summary_df.columns]
    navy_summary_df = navy_summary_df.rename(
        columns={
            "Country": "country",
            "Installation": "installation",
            "Category": "category",
            "FY16": "fy16",
            "FY17": "fy17",
            "FY18": "fy18",
            "FY19": "fy19",
            "FY20": "fy20",
            "FY21": "fy21",
            "FY22": "fy22",
            "FY23": "fy23",
            "FY23 thru SEP": "fy23_thru_sep",
            "ANNUALIZED FY23": "annualized_fy23",
            "FY24 thru APR": "fy24_thru_apr",
            "ANNUALIZED FY24": "annualized_fy24",
            "Latitude": "base_latitude",
            "Longitude": "base_longitude",
        }
    )
    numeric_cols = [
        "fy16",
        "fy17",
        "fy18",
        "fy19",
        "fy20",
        "fy21",
        "fy22",
        "fy23",
        "fy23_thru_sep",
        "annualized_fy23",
        "fy24_thru_apr",
        "annualized_fy24",
        "base_latitude",
        "base_longitude",
    ]
    for col in numeric_cols:
        navy_summary_df[col] = pd.to_numeric(navy_summary_df[col], errors="coerce")
    navy_summary_df = navy_summary_df.where(pd.notnull(navy_summary_df), None)
    navy_summary_columns = [
        "country",
        "installation",
        "category",
        "fy16",
        "fy17",
        "fy18",
        "fy19",
        "fy20",
        "fy21",
        "fy22",
        "fy23",
        "fy23_thru_sep",
        "annualized_fy23",
        "fy24_thru_apr",
        "annualized_fy24",
        "base_latitude",
        "base_longitude",
    ]
    navy_summary_records = navy_summary_df[navy_summary_columns].to_dict(orient="records")
    db[NAVY_SUMMARY_TABLE].insert_all(
        navy_summary_records,
        column_order=navy_summary_columns,
        batch_size=500,
    )
    navy_summary_table = db[NAVY_SUMMARY_TABLE]
    for col in ("country", "installation", "category"):
        navy_summary_table.create_index([col], if_not_exists=True)

    # Load Navy monthly CSV.
    navy_monthly_df = pd.read_csv(NAVY_MONTHLY_CSV_PATH)
    navy_monthly_df.columns = [c.strip() for c in navy_monthly_df.columns]
    navy_monthly_df = navy_monthly_df.rename(
        columns={
            "Installation": "installation",
            "Loc#": "loc_id",
            "Location": "location_name",
            "Month": "month_label",
            "Revenue": "revenue",
            "NAFI Amount": "nafi_amount",
            "Annual Revenue": "annual_revenue",
            "Annual NAFI": "annual_nafi",
            "Status": "status",
        }
    )
    navy_monthly_df["revenue"] = pd.to_numeric(navy_monthly_df["revenue"], errors="coerce")
    navy_monthly_df["nafi_amount"] = pd.to_numeric(navy_monthly_df["nafi_amount"], errors="coerce")
    navy_monthly_df["annual_revenue"] = pd.to_numeric(navy_monthly_df["annual_revenue"], errors="coerce")
    navy_monthly_df["annual_nafi"] = pd.to_numeric(navy_monthly_df["annual_nafi"], errors="coerce")
    navy_monthly_df["loc_id"] = pd.to_numeric(navy_monthly_df["loc_id"], errors="coerce").astype("Int64")
    navy_monthly_df = navy_monthly_df.where(pd.notnull(navy_monthly_df), None)
    navy_monthly_columns = [
        "installation",
        "loc_id",
        "location_name",
        "month_label",
        "revenue",
        "nafi_amount",
        "annual_revenue",
        "annual_nafi",
        "status",
    ]
    navy_monthly_records = navy_monthly_df[navy_monthly_columns].to_dict(orient="records")
    db[NAVY_MONTHLY_TABLE].insert_all(
        navy_monthly_records,
        column_order=navy_monthly_columns,
        batch_size=500,
    )
    navy_monthly_table = db[NAVY_MONTHLY_TABLE]
    for col in ("installation", "location_name", "month_label"):
        navy_monthly_table.create_index([col], if_not_exists=True)

    print(f"Wrote {len(navy_summary_records)} navy summary records to {DB_PATH}")
    print(f"Wrote {len(navy_monthly_records)} navy monthly records to {DB_PATH}")


if __name__ == "__main__":
    main()
