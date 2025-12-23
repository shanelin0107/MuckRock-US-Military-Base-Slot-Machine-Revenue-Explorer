# Data Dictionary — Military Base Revenue Data

Last updated: 2025-12-08  
Source: MuckRock FOIA request covering FY2020–FY2024 military base revenue, asset, and financial disclosures.

---

## `District_Revenue_FY20-FY24_with_lat_lon_clean.csv`

**Primary dataset**: District-level revenue aggregation by service branch and base.

| Column | Type | Description | Example |
| --- | --- | --- | --- |
| `Service` | TEXT | Military service branch (`Navy`, `USMC`, `Army`, etc.). | `Navy` |
| `Category` | TEXT | Ledger category (typically `Revenue`). | `Revenue` |
| `Region` | TEXT | Geographic district or theater (e.g., `Japan`, `Europe`, `Korea`). | `Japan` |
| `Base` | TEXT | Military installation name (standardized). | `Camp Foster` |
| `Location` | TEXT | Specific venue or facility within the base. | `Ocean Breeze` |
| `Month` | TEXT | Month name (full, e.g., `January`, `September`). | `September` |
| `Year` | INTEGER | Calendar year. | `2024` |
| `Amount` | REAL | Revenue amount (USD). Can be negative for refunds/adjustments. | `45678.32` |
| `Base_lat` | REAL | Latitude coordinate for mapping/cluster visualization. | `26.3421` |
| `Base_lon` | REAL | Longitude coordinate for mapping/cluster visualization. | `127.8016` |

### Notes
- One row per base–location–month–year combination.
- GPS coordinates enable Datasette cluster map visualization.

---

## `Marine_Revenue_FY20-FY24_detail_with_gps.csv`

**Marine Corps revenue**: Per-facility, per-month revenue including slot machine and NAFI amounts.

| Column | Type | Description | Example |
| --- | --- | --- | --- |
| `Page` | INTEGER | Original PDF page reference (extraction tracking). | `42` |
| `Loc #` | TEXT | Facility location identifier or code. | `JP-001` |
| `Base` | TEXT | Military installation name. | `Camp Foster` |
| `Location` | TEXT | Venue or facility name. | `Ocean Breeze` |
| `Month` | TEXT | Month name. | `September` |
| `Revenue` | REAL | Slot machine revenue for that month. | `12345.67` |
| `NAFI Amount` | REAL | Morale, Welfare & Recreation (MWR/NAFI) revenue. | `5432.10` |
| `Annual Revenue` | REAL | Year-to-date slot machine revenue (running total). | `123456.78` |
| `Annual NAFI` | REAL | Year-to-date NAFI/MWR revenue (running total). | `54321.09` |
| `Latitude` | REAL | Decimal latitude for mapping. | `26.3421` |
| `Longitude` | REAL | Decimal longitude for mapping. | `127.8016` |

### Notes
- Separates slot machine revenue from NAFI/MWR revenue for operational clarity.
- Annual columns are running totals within each fiscal or calendar year.
- GPS coordinates support Datasette cluster map and spatial analysis.

---

## `Navy Revenue Report FY20-FY24-2_monthly_summary.csv`

**Navy revenue summary**: Monthly aggregation by installation and facility.

| Column | Type | Description | Example |
| --- | --- | --- | --- |
| `Installation` | TEXT | Naval installation name. | `Yokosuka Naval Base` |
| `Loc#` | TEXT | Facility location identifier. | `JP-NW-001` |
| `Location` | TEXT | Venue or facility name. | `Fleet Club` |
| `Month` | TEXT | Month name. | `July` |
| `Revenue` | REAL | Slot machine or primary revenue stream. | `23456.00` |
| `NAFI Amount` | REAL | NAFI/MWR revenue for that month. | `8765.50` |
| `Annual Revenue` | REAL | Year-to-date primary revenue. | `234560.00` |
| `Annual NAFI` | REAL | Year-to-date NAFI revenue. | `87655.00` |
| `Status` | TEXT | Data status note (e.g., `Complete`, `Partial`, `Estimated`). | `Complete` |

### Notes
- Aggregated monthly summary derived from Navy financial statements.
- `Status` field indicates data completeness and extraction confidence.
- Columns may vary across fiscal years depending on original reporting structure.

---

## `Navy_Revenue_Reimburse_Summary_updated.csv`

**Navy reimbursements**: Fiscal-year-level reimbursement and NAFI payments by country/installation.

| Column | Type | Description | Example |
| --- | --- | --- | --- |
| `Country` | TEXT | Country or region where installation is located. | `Japan` |
| `Installation` | TEXT | Naval installation name. | `Naval Station Rota` |
| `Category` | TEXT | Record category (e.g., `Reimbursement`, `NAFI`, `Adjustment`). | `Reimbursement` |
| `FY16` – `FY24 thru APR` | REAL | Fiscal year columns (FY16, FY17, ..., FY24 thru APR). One entry per FY. | `5432.10` |
| `ANNUALIZED FY23` | REAL | Annualized projection for FY2023 (full 12 months). | `54321.00` |
| `ANNUALIZED FY24` | REAL | Annualized projection for FY2024 (full 12 months). | `65432.00` |
| `Latitude` | REAL | Decimal latitude for mapping. | `36.6410` |
| `Longitude` | REAL | Decimal longitude for mapping. | `-5.3550` |

### Notes
- Wide format: each fiscal year is a separate column for easier year-over-year comparison.
- Reimbursement data reflects Navy-specific NAFI remittances and reconciliation entries.
- Partial-year columns (e.g., `FY23 thru SEP`, `FY24 thru APR`) reflect reporting cutoffs.
- Annualized columns provide full-year estimates for incomplete fiscal years.
- GPS coordinates enable location-based filtering and analysis in Datasette.

