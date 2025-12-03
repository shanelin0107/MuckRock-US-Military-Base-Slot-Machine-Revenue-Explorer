# Data Dictionary — `slot_machine_revenue`

Last updated: 2025-11-19  
Source: MuckRock FOIA request covering FY2020–FY2024 slot machine disclosures.

| Column | Type | Description | Example |
| --- | --- | --- | --- |
| `installation_name` | TEXT | Canonical name of the military installation. | `Camp Foster` |
| `facility_name` | TEXT | Venue or building operating the slot machines. | `Ocean Breeze` |
| `branch` | TEXT | Military branch reporting the revenue (`Army`, `Navy`, `USMC`). | `Navy` |
| `district` | TEXT | Geographic district or theater label from the FOIA files (e.g., `Japan`, `Europe`, `Korea`). | `Japan` |
| `category` | TEXT | Ledger category (primarily `Revenue`). | `Revenue` |
| `calendar_year` | INTEGER | Calendar year listed in the PDF report. | `2024` |
| `fiscal_year` | INTEGER | U.S. federal fiscal year derived from month and calendar year. | `2024` |
| `month_name` | TEXT | Month text from the source (capitalized). | `September` |
| `month_number` | INTEGER | Numeric month index (1–12) for ordering and fiscal logic. | `9` |
| `revenue` | REAL | Dollar amount reported for that facility-month (positive or negative). | `45678.32` |
| `latitude` | REAL | Decimal latitude used for Datasette cluster map. | `26.3421` |
| `longitude` | REAL | Decimal longitude used for Datasette cluster map. | `127.8016` |

### Indexes
- `branch`
- `district`
- `fiscal_year`
- `installation_name`

### Notes
- Fiscal years roll over each October (Oct–Dec records are counted toward the next FY).
- Revenue values can be negative if refunds or adjustments were recorded for the month.
- District values can represent broad theaters (e.g., `Europe`) when base-level country details were not provided in the PDFs.
