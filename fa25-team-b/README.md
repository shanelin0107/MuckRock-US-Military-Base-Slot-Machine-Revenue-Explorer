
<h1 align="center">
  <br>
  <a href="https://www.bu.edu/spark/" target="_blank"><img src="https://www.bu.edu/spark/files/2023/08/logo.png" alt="BUSpark" width="200"></a>
  <br>
  ARMP Slot Machine Revenue Analysis
  <br>
</h1>

<h4 align="center">Analyzing U.S. Military Slot Machine Revenues and Gambling Risks Across Overseas Bases</h4>

<p align="center">
  <a href="#key-features">Key Features</a> •
  <a href="#how-to-use">How To Use</a> •
  <a href="#project-description">Project Description</a> •
  <a href="#preliminary-analysis-and-results">Preliminary Analysis & Results</a> •
  <a href="#data-locations">Data Locations</a>
</p>

## Key Features

This repository contains a complete pipeline for extracting, cleaning, analyzing, and visualizing slot machine revenue data from the Army Recreation Machine Program (ARMP). Below is an overview of the key components:

### **PDF Extraction Pipeline**
* **` PDF Extraction/`** - Automated extraction scripts for converting unstructured PDF reports into structured CSV datasets
  - Handles multiple report types: Asset Reports (FY2020–FY2024), Marine Revenue, Navy Revenue, Financial Statements, District Revenues, and Revenue Comparison
  - Uses multiple parsing tools (pdfplumber, PyMuPDF, Camelot, Tabula, poppler-utils) depending on document complexity
  - [See detailed extraction documentation](./PDF%20Extraction/readme.md)
  - Key extraction notebooks:
    - `FY2020+2023+2024_Asset_Report.ipynb` - Extracts 8 standardized tables from Asset Reports
    - `FY2021_Asset_Report_Extraction.ipynb` - Handles COVID-specific formatting in FY2021 data
    - `FY2022_Asset_Report_Extraction.py` - Python script for FY2022 extraction
    - `Marine_Revenue_FY20_FY24.ipynb` - Marine Corps revenue extraction with adjustable parameters
    - `navy_revenue_report-1.py` & `navy_revenue_report-2.py` - Navy revenue parsing scripts
    - `District_Revenues_FY20_FY24.ipynb` - Multi-region district revenue extraction
    - `parseFinancialStatements.py` - Financial statement OCR and extraction

### **Exploratory Data Analysis (EDA)**
* **`eda/`** - Comprehensive analysis notebooks examining revenue patterns, trends, and distributions
  - `Financial_Statements_EDA.ipynb` - Cash flow and asset depreciation analysis
  - `Revenue_Comparison_EDA.ipynb` - Cross-region and cross-branch revenue comparisons
  - `Project_Base_Question_2.ipynb` - Top revenue-generating bases by year and service branch
  - `Marine_Revenue_FY20_FY24.ipynb` - Marine Corps revenue trends and seasonal patterns
  - `Asset_Report_2024_Region_Service_EDA.ipynb` - EGM distribution by region and service
  - `FY2021_Asset_Report_EDA.ipynb` - Asset distribution and COVID-era reporting validation
  - `navy_report-1.ipynb` - Navy revenue trends by country and installation (FY16–FY22)
  - `navy_revenue_report-2.ipynb` - Detailed Navy monthly revenue analysis (FY18–FY24)
  - [See EDA findings summary](./eda/README.md)

### **Project Documentation**
* **`project_definition.md`** - Official project scope, objectives, and deliverables
* **`research.md`** - Research sources on military gambling addiction and policy impacts
* **`README.md`** - This file; comprehensive project overview and documentation


## How To Use

### Prerequisites
You'll need the following installed:
- <a href="https://git-scm.com" target="_blank">Git</a>
- Python 3.8 or higher
- Jupyter Notebook or JupyterLab

### Clone and Setup

```bash
# Clone this repository
$ git clone [repo link]

# Navigate to the project directory
$ cd fa25-team-b

# Install required Python packages
$ pip install -r " PDF Extraction/requirements.txt"
```

### Running PDF Extraction

Each PDF extraction script is designed for a specific report type. Navigate to the ` PDF Extraction/` directory and run the appropriate notebook or script:

```bash
# For Jupyter notebooks (recommended)
$ jupyter notebook " PDF Extraction/Marine_Revenue_FY20_FY24.ipynb"

# For Python scripts
$ python " PDF Extraction/navy_revenue_report-1.py"
```

**Note:** Some extraction scripts require manual file path configuration. Update the file paths in the notebooks to point to your local PDF files.

For detailed extraction procedures and parameters, see the [PDF Extraction README](./PDF%20Extraction/readme.md).

### Running Exploratory Data Analysis

EDA notebooks are located in the `eda/` directory. Each notebook is self-contained and includes visualizations:

```bash
# Open the EDA directory in Jupyter
$ jupyter notebook eda/

# Or run a specific notebook
$ jupyter notebook eda/Project_Base_Question_2.ipynb
```

### Git Workflow

Create a new branch from main for any changes:

```bash
# Create and checkout a new branch
$ git checkout -b your-branch-name main

# Make your changes, then commit
$ git add .
$ git commit -m "Description of changes"

# Push your branch
$ git push origin your-branch-name
```

Open a Pull Request and add your PM and TPM as reviewers. At the end of the semester, open a final Pull Request to main from the dev branch.


## Project Description

### Problem Statement
Slot machines on overseas U.S. military bases generate tens of millions of dollars in annual revenue, yet there is little transparency into how this money is distributed across bases, branches, and regions, or what it implies for the gambling risks faced by service members. Without clear, accessible analysis, policymakers and the public cannot fully understand which bases present the highest risks, which games are most associated with addiction, or how revenue trends have evolved over time. This lack of insight hinders informed oversight and limits the ability to address potential gambling-related harms within the military.

### Data
The data for this project comes from the **Army Recreation Machine Program (ARMP)**, which currently operates **1,889 slot machines across 79 overseas military bases** and generated **$70.9 million in revenue during FY2024**.

MuckRock has obtained a cache of official records delivered as unstructured PDFs containing tabular financial and asset information. The available documents include:

- District Revenues (FY2020–FY2024)
- Financial Statements
- Annual Asset Reports (FY2020–FY2024)
- Marine Revenue Reports (FY2020–FY2024)
- Navy Revenue Reports (FY2020–FY2024)
- Revenue Comparison Reports
- Presentations and supporting files

### Project Objectives / Goals
- Extract, clean, and standardize ARMP slot machine records into a structured dataset
- Deploy a SQLite/Datasette interface that enables interactive browsing and visualization of revenues
- Explore patterns of revenue distribution, trends over time, and game types linked to gambling risks
- Provide recommendations to support transparency and responsible gaming practices

### Scope
The scope of this project includes:
- Data extraction from PDFs
- Cleaning and normalization of records
- Exploratory analysis of slot machine revenues
- Data visualization
- Database deployment for public access
- Report preparation summarizing findings and recommendations

### Deliverables
- A cleaned and documented dataset of ARMP slot machine revenues
- A reproducible extraction and cleaning pipeline in Python
- A deployed SQLite/Datasette instance for browsing and visualization
- A written report summarizing findings, limitations, and recommendations

## Preliminary Analysis and Results

Our exploratory data analysis has revealed significant patterns in slot machine revenue distribution, regional concentration, and temporal trends across overseas U.S. military installations. Key findings are summarized below:

### Geographic and Branch Distribution

**Regional Concentration:**
- **Europe** dominates total slot machine operations with 39.4% of all Electronic Gaming Machines (EGMs), followed closely by **Japan** (37.8%) and **Korea** (22.8%)
- However, revenue patterns differ from machine distribution: **Europe generates ~$41M annually** (highest total), while the **Far East (Japan + Korea) contributes ~$30M**
- Analysis location: `eda/Asset_Report_2024_Region_Service_EDA.ipynb`

**Service Branch Leadership:**
- The **Army operates 55.7% of all EGMs**, making it the primary service managing gambling operations
- **Navy** accounts for 25.4% and **Marine Corps** 19.0% of total machines
- **Air Force** has no recorded EGMs in the dataset
- Analysis location: `eda/Asset_Report_2024_Region_Service_EDA.ipynb`

### Top Revenue-Generating Bases

**Overall Leaders (FY2020–FY2024 cumulative):**
1. **Camp Butler / Foster (USMC, Japan)** - $70.6M
2. **Camp Humphreys (Army, Korea)** - $60.9M
3. **Yokosuka Navy (Japan)** - $36.5M
4. **AFRC Dragon Hill Lodge (Army, Korea)** - $24.3M
5. **Sasebo Navy (Japan)** - $16.2M

**Key Observations:**
- Asia-Pacific installations (Japan and Korea) account for over **70% of total ARMP revenue**
- Each service branch is anchored by one dominant installation: Camp Humphreys (Army), Yokosuka (Navy), and Camp Butler/Foster (Marine Corps)
- Analysis location: `eda/Project_Base_Question_2.ipynb`

### Temporal Trends

**COVID-19 Impact:**
- All branches experienced a **sharp revenue decline in FY2020** due to pandemic-related restrictions
- Recovery began in FY2021 and peaked in **FY2023** across most installations
- Analysis locations: `eda/Marine_Revenue_FY20_FY24.ipynb`, `eda/navy_report-1.ipynb`

**Seasonal Patterns:**
- Marine Corps bases show **higher gambling activity in March and May**, a trend requiring further investigation
- Navy installations in Japan (particularly Yokosuka and Sasebo) demonstrate **consistent growth from FY2016–FY2023**, with Yokosuka nearly doubling its revenue during this period
- Analysis locations: `eda/Marine_Revenue_FY20_FY24.ipynb`, `eda/navy_revenue_report-2.ipynb`

**Recent Trends:**
- FY2024 data shows a synchronized downturn across all branches, attributed to **incomplete fiscal data** rather than operational decline
- Analysis location: `eda/Project_Base_Question_2.ipynb`

### Financial Health

**Cash Flow Analysis:**
- Total operational cash grew steadily from 2020 until early 2023, then declined sharply due to **complete depletion of restricted cash reserves**
- **Total equity has remained unchanged** (to the cent) since October 31, 2021, raising questions about financial reporting practices
- Analysis location: `eda/Financial_Statements_EDA.ipynb`

**Asset Trends:**
- Combined asset values (accounting for depreciation) declined from **~$16M in 2020 to under $7M by end of 2022**, before recovering to **$20M by April 2024**
- Recovery driven by both decreased depreciation and increased asset acquisitions
- Analysis location: `eda/Financial_Statements_EDA.ipynb`

### Revenue Per Base and Per Machine

**Efficiency Metrics:**
- **Japan Navy bases** generate the highest revenue per installation ($730,765/base), followed by Marine Corps Japan bases ($680,042/base)
- **Revenue per machine** varies significantly: Japan Navy machines average $118.40, while Korea Navy machines generate only $46.10
- European Army bases show moderate performance at $80.06 per machine
- Analysis location: `eda/Revenue_Comparison_EDA.ipynb`

**Manufacturer Contributions:**
- When machine counts are combined with per-machine revenue estimates, **NOV and BAL manufacturers** contribute the most revenue overall
- **IGT, AIN, and ITC** also play significant roles in total revenue generation
- Analysis location: `eda/Revenue_Comparison_EDA.ipynb`

### Methodological Notes

- **FY2021 Data:** Required custom parsing due to COVID-specific reporting categories and irregular table formatting (see `eda/FY2021_Asset_Report_EDA.ipynb`)
- **Navy Revenue Extraction Issues:** Extremely small font sizes and damaged numeric fields in PDF reports (particularly for Yokosuka, Souda Bay, Sasebo, and Atsugi) caused extraction challenges that have been raised with the client
- **Revenue Estimation:** Per-base and per-manufacturer revenue estimates assume uniform revenue per machine within each region/branch combination

For complete analysis details, visualizations, and code, please refer to the individual notebooks in the `eda/` directory and the [EDA README](./eda/README.md).

## Data Locations

All data for this project originates from official ARMP records obtained by MuckRock as unstructured PDF files. Due to file size and privacy considerations, raw PDFs are not included in this repository.

### Extracted Datasets (CSV Outputs)

Generated CSV files from the extraction pipeline include:

**Asset Reports:**
- `assets_by_region_service.csv` - Summary of assets by region and service
- `assets_by_field_office.csv` - Asset and EGM counts by field office
- `installed_assets_location_manufacture.csv` - Installed assets by manufacturer and service
- `asset_details.csv` - Detailed asset listings with serial numbers and acquisition dates
- `floor_asset_details.csv` - Floor-level installation details
- `site_operational_status.csv` - Site operational status and service affiliation
- `years_in_storage.csv` - Asset age versus years in storage

**Revenue Reports:**
- `Marine_Revenue_FY20-FY24_summary table.csv` - Marine Corps revenue by country and installation
- `Marine_Revenue_FY20-FY24_detail.csv` - Monthly Marine Corps revenue details
- `Navy_Revenue_Table.csv` - Navy revenue by country and installation (FY18–FY24)
- `Navy_Monthly_Revenue_Report.csv` - Detailed monthly Navy revenues by installation
- `District_Revenue_filtered_FY20-FY24_final.csv` - Multi-region district revenue data
- `FinancialStatement.csv` - Financial statements with cash flow and asset data

**Revenue Comparison:**
- `Revenue Comparison_C.xlsx` - Consolidated revenue comparison workbook (manually extracted via Adobe Express)

### Documentation
- <a href="./PDF%20Extraction/readme.md">PDF Extraction Detailed Documentation</a> - Complete extraction procedures and methodology
- <a href="./eda/README.md">EDA Findings Summary</a> - Detailed analysis findings and visualizations
- <a href="./project_definition.md">Project Definition</a> - Official project scope and objectives
- <a href="./research.md">Research Sources</a> - Academic and policy research on military gambling
