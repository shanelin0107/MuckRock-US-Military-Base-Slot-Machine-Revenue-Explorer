# Exploratory Data Analysis (EDA) — Army Recreation Machine Program (ARMP)

## Overview

This folder contains comprehensive exploratory data analyses of slot machine operations across U.S. military installations worldwide. The analyses cover financial statements, asset distributions, revenue patterns, and operational trends across multiple fiscal years (FY2016–FY2024).

## Project Structure

The EDA is organized into eight Jupyter notebooks, each focusing on specific aspects of the ARMP data:

### 1. Financial Statements Analysis (`Financial_Statements_EDA.ipynb`)

**Objective**: Analyze the overall financial health and cash flow trends of the ARMP.

**Key Findings**:
- **Cash Holdings**: Operational and restricted cash grew steadily from 2020 until early 2023, then declined sharply due to complete depletion of restricted cash reserves.
- **Total Equity**: Remained at exactly the same value (to the cent) since 10/31/2021, raising questions about financial reporting practices.
- **Asset Depreciation**: Combined asset values declined from ~$16M (2020) to under $7M (end of 2022), before rebounding to $20M by April 2024.

**Data Source**: FinancialStatement.csv

---

### 2. Revenue Comparison Analysis (`Revenue_Comparison_EDA.ipynb`)

**Objective**: Compare slot machine revenues across service branches and geographic regions.

**Key Findings**:
- **Regional Distribution**: Europe generates the largest total revenue (~$41M), followed by Far East (~$30M).
- **Per-Base Revenue**: Japan's Navy and Marine Corps bases generate higher revenue per base than European counterparts.
- **Top Performers**: Japanese installations (Ocean Breeze, Taiyo G/C, Palms) and European sites (La Plaza, Graf E/C) rank as top revenue generators.
- **External Validation**: FY2024 revenue reached $70.9M, up from $64.8M in FY2023.

**Methodology**: Revenue-per-machine estimates derived by dividing regional totals by machine counts from FY2021 Asset Report.

**Data Source**: Revenue Comparison spreadsheet (FY2023-2024)

---

### 3. District Revenue Analysis (`District_Revenue_EDA.ipynb`)

**Objective**: Identify which military bases generate the highest slot machine revenues and track ranking changes over time.

**Key Findings**:
- **Top Revenue Bases (FY2020-FY2024)**:
  1. Camp Butler/Foster (USMC, Japan): $70.6M cumulative
  2. Camp Humphreys (Army, Korea): $60.9M cumulative
  3. Yokosuka Navy (Japan): $36.5M cumulative
- **Geographic Dominance**: Asia-Pacific installations (Japan + Korea) account for >70% of global ARMP revenue.
- **Peak Performance**: Most top bases peaked in FY2023 (~$15-18M), with FY2024 showing decline due to incomplete data.
- **Branch Leadership**: Army bases collectively generate nearly 60% of global revenue.
- **Seasonal Trends**: Moderate year-to-year fluctuations suggest stable demand, with emerging growth in European bases (Kaiserslautern, Wiesbaden) post-COVID.

**Data Source**: District_Revenue_filtered_FY20-FY24_final.csv

---

### 4. FY2021 Asset Report Analysis (`EGM_Analysis_by_Region_Manufacturer_EDA.ipynb`)

**Objective**: Understand slot machine inventory patterns, manufacturer distribution, and installation trends.

**Key Findings**:
- **Regional Distribution**:
  - Europe: 126k Army machines + 20k Navy machines across 20+ bases
  - Japan: 102k Marine Corps machines across 12 bases
  - Korea: 107k Army machines across 14 bases
- **Manufacturer Dominance**: NOV (Novomatic) and BAL (Bally) supply majority of machines, followed by IGT, AIN, and ITC.
- **Installation Timeline**: Large batches installed in early 2000s; ACM/ITC machines peaked 2003-2006; SLOT machines peaked 2015-2017.
- **Machine Age**: Significant aging of inventory observed, with depreciation trends affecting asset values.

**Data Source**: FY2021_Asset_Report.xlsx (Installed_Assets, Field_Office, Asset_Details, Floor_Details sheets)

---

### 5. FY2024 EGM Distribution Analysis (`EGM_Distribution_EDA.ipynb`)

**Objective**: Analyze current Electronic Gaming Machine (EGM) distribution across regions and service branches.

**Key Findings**:
- **Regional Shares**: Europe (39.4%), Japan (37.8%), Korea (22.8%)
- **Service Branch Composition**: Army (55.7%), Navy (25.4%), Marine Corps (19.0%), Airforce (0%)
- **Monthly Trends**: Europe maintains consistently higher EGM counts; Korea shows slight mid-year decline with year-end recovery.
- **Regional Specialization**: Europe leads in Army-operated EGMs; Japan dominates in Marine Corps EGMs.

**Data Extraction**: Parsed from FY2024 Asset Report PDF using Python (pdfplumber) pipeline.

**Data Source**: egms_by_region_service_2024.csv

---

### 6. Marine Corps Revenue Analysis (`Marine_Revenue_EDA.ipynb`)

**Objective**: Examine revenue patterns specifically for Marine Corps installations.

**Key Findings**:
- **Top Performers**: Top 3 Marine bases generate significantly higher mean slot machine revenue than other installations.
- **COVID-19 Impact**: Sharp revenue drop in 2020, with gradual recovery through 2024.
- **Seasonal Patterns**: Clear peaks in March and May across all years, suggesting seasonal engagement patterns among service members.
- **Geographic Concentration**: Majority of Marine Corps revenue concentrated in Japan installations.

**Data Cleaning**:
- Removed outliers using IQR method
- Standardized currency values (removed $, commas, handled negative parentheses)
- Normalized month/date formats to YYYY-MM standard
- NAFI Amount identified as fixed proportion of revenue (excluded from analysis)

**Data Source**: Marine_Revenue_FY20-FY24_detail.csv

---

### 7. Navy Slot vs NAFI Comparison (`Navy_Slot_NAFI_Revenue_Comparison_EDA.ipynb`)

**Objective**: Compare Navy slot machine revenues with NAFI (Non-Appropriated Fund Instrumentality) reimbursements.

**Key Findings**:
- **Growth Trend**: Both Slot Revenue and NAFI Reimbursements show increasing trend FY16-FY22, with FY22 recording highest totals.
- **Country Dominance**: Japan far surpasses all other countries in both categories; Italy and Spain rank distant second/third.
- **Time Trends**: Japan maintains highest revenue levels with steady growth after temporary FY20 decline (COVID-19).
- **Stability**: Italy and Spain demonstrate moderate but stable contributions throughout the period.

**Data Sources**: navy_slot_results.csv, navy_nafi_reimbursements.csv

---

### 8. Navy Revenue by Installation (`Navy_Slot_Revenue_by_Installation_EDA.ipynb`)

**Objective**: Identify top-performing Navy installations and track revenue trends by location.

**Key Findings**:
- **Highest Average Revenue per Installation**: Japan-based installations generate significantly higher average revenue than other countries.
- **Top Two Installations**: Yokosuka and Sasebo (both Japan) dominate Navy slot revenues FY18-FY24.
- **Trend Stability**: Top installations show consistent performance with moderate growth through FY23.
- **Geographic Insight**: Japanese-based Navy installations are key contributors to overall overseas slot revenue.

**Data Sources**: Navy Revenue Table (by country/installation FY18-FY24), Monthly Revenue Report (detailed monthly breakdown)

---

## Data Sources Summary

| Dataset | Fiscal Years | Format | Primary Use |
|---------|--------------|--------|-------------|
| Financial Statements | 2020-2024 | CSV | Cash flow, equity, asset depreciation |
| Revenue Comparison | 2023-2024 | Excel | Regional/branch revenue totals |
| District Revenue | 2020-2024 | CSV | Base-level revenue rankings |
| FY2021 Asset Report | 2021 | Excel | Machine inventory, manufacturers |
| FY2024 Asset Report | 2024 | PDF → CSV | Current EGM distribution |
| Marine Revenue | 2020-2024 | CSV | Marine Corps installation revenues |
| Navy Slot/NAFI | 2016-2022 | CSV | Navy revenue and reimbursements |
| Navy Installation Revenue | 2018-2024 | CSV | Navy base-level performance |

---

## Key Cross-Cutting Findings

### Geographic Patterns
- **Asia-Pacific Dominance**: Japan and Korea installations generate >70% of total ARMP revenue
- **Japan's Central Role**: Highest revenues across all service branches; top performer in Navy and Marine Corps categories
- **Europe's Significance**: Largest share of EGMs (39.4%); strongest Army presence

### Service Branch Patterns
- **Army Dominance**: Operates 55.7% of all EGMs; generates ~60% of global revenue
- **Marine Corps Concentration**: Highest per-base revenue; concentrated in Japan
- **Navy Distribution**: Strong presence in Japan (Yokosuka, Sasebo lead); moderate European operations

### Temporal Trends
- **COVID-19 Impact**: Sharp revenue decline in FY2020 across all branches
- **Recovery Pattern**: Gradual revenue recovery FY2021-FY2023
- **FY2024 Decline**: Attributed to incomplete fiscal year data rather than operational decline
- **Seasonal Patterns**: March and May show consistent revenue peaks

### Financial Health Concerns
- **Restricted Cash Depletion**: Complete drawdown of restricted cash reserves by 2023
- **Static Equity**: Total equity unchanged since October 2021 (potential reporting issue)
- **Asset Aging**: Significant machine inventory aging; depreciation trends require attention

---

## Methodology Notes

### Data Cleaning Procedures
1. **Currency Values**: Removed $, commas, and special characters; converted parentheses to negative values
2. **Date Normalization**: Standardized to YYYY-MM format using pandas datetime parsing
3. **Outlier Handling**: Applied IQR method to remove extreme values in revenue distributions
4. **Missing Data**: Filled with 0.0 for financial values; empty strings for categorical data
5. **Duplicate Removal**: Deduplicated rows across all datasets

### Estimation Methods
- **Revenue per Machine**: Calculated by dividing regional/branch totals by machine counts from asset reports
- **Base-Level Revenue**: Estimated by multiplying machine counts by revenue-per-machine within region/branch
- **Annualized Values**: Partial-year data scaled to full fiscal year where noted

### Limitations
- **Incomplete FY2024 Data**: Final fiscal year data not complete at time of analysis
- **Estimation Assumptions**: Revenue-per-machine calculations assume uniform performance within region/branch
- **Parsing Challenges**: FY2021 data required extensive cleaning due to PDF formatting irregularities
- **Missing Revenue Details**: Financial Statements analysis limited to partial Asset/Liability Balance data

---

## Visualization Highlights

Each notebook includes multiple visualizations:
- **Bar Charts**: Total revenues by year, country, region, and service branch
- **Line Charts**: Time-series trends for revenues, cash holdings, and asset values
- **Pie Charts**: Regional and service branch composition of EGMs and revenues
- **Stacked/Grouped Charts**: Multi-dimensional comparisons across categories
- **Distribution Plots**: Revenue distributions with KDE overlays

---

## Usage Instructions

### Prerequisites
```bash
pip install pandas numpy matplotlib seaborn openpyxl
```

### Running the Notebooks
1. Ensure all CSV/Excel data files are in the correct directory paths
2. Update file paths in notebook cells to match your local environment
3. Run cells sequentially to reproduce analyses
4. Visualizations will display inline in Jupyter environment

### Replication Notes
- All notebooks use reproducible methods where applicable
- Data extraction code (for PDF parsing) provided in FY2024 EGM Distribution notebook
- Cleaning functions documented at top of each notebook

---

## Contributors

This EDA was conducted by Team B for DS701 course, with each member contributing specialized analyses across Financial Statements, Revenue Comparisons, District Revenue, Asset Reports, Marine Corps Revenue, and Navy Revenue analyses.

---

## External References

- **FY2024 Revenue Report**: ARMP raised $70.9M in FY2024, up from $64.8M in FY2023
- **Camp Humphreys**: Generated >$6M between October 2024 and May 2025 (news article reference)
- **NAFI Definition**: Non-Appropriated Fund Instrumentality - funds derived from slot machine revenues

---

## Future Work

Potential extensions of this analysis:
1. **Predictive Modeling**: Forecast future revenues based on historical trends
2. **Causal Analysis**: Investigate drivers of seasonal patterns (March/May peaks)
3. **Comparative Analysis**: Compare ARMP performance against commercial casino benchmarks
4. **Policy Evaluation**: Assess impact of regulatory changes on revenue trends
5. **Integration**: Combine all fiscal years into unified longitudinal dataset
6. **Financial Health**: Investigate static equity value and cash depletion patterns

---

## Contact

For questions about this EDA, please contact the DS701 Team B members or refer to individual notebook documentation.
