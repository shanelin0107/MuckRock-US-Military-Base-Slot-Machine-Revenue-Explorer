
# Project Datasheet: MuckRock US Military Base Slot Machine Revenue Explorer

## 1. Project Information

**What is the project name?**
> **MuckRock: US Military Base Slot Machine Revenue Explorer**

**Team Members**
> *   Cameron Moore
> *   Ching Hsuan Lin
> *   Jyun-Ru Huang
> *   Nithya Priya Jayakumar
> *   Pin-Hao Pan
> *   Quoc Dat Nguyen

**What is the link to your project's GitHub repository?**
> *https://github.com/BU-Spark/ds-muckrock-liberation/tree/fa25-team-b-dev/fa25-team-b*

**What is the link to your project's Google Drive folder?**
> [Spark! Owned Google Drive Folder](https://drive.google.com/drive/folders/1CZ0JF2y9IhaPy-KH4tkH2YbJyr750urc?usp=drive_link)

**In your own words, what is this project about? What is the goal of this project?**
> This project is a data liberation initiative centering on the **Army Recreation Machine Program (ARMP)**, which operates approximately **1,889 slot machines across 79 overseas US military bases**.
>
> **Project Objectives:**
> 1.  **Data Extraction and Cleaning:** Develop automated, reproducible Python pipelines to transform 14 highly unstructured, multi-format PDF reports into analysis-ready CSV files.
> 2.  **Cloud Deployment:** Build and deploy a cloud-based **Datasette** instance to enable journalists and the public to query and visualize the data.
> 3.  **Gambling Risk Analysis:** Conduct in-depth analysis to reveal revenue distribution, identify high-risk installations, and track temporal trends (including COVID-19 impacts and machine inventory surges).

**Who is the client for the project?**
> **MuckRock Foundation**

**What class was this project part of?**
> **DS 701: Tools for Data Science (Spark!) - Fall 2025 (FA25), Boston University**

---

## 2. Dataset Information

**What data sets did you use in your project?**
The project processed multiple PDF reports provided by MuckRock via FOIA requests.

1.  **Asset Reports** (FY2020–FY2024): Inventory data including manufacturers, serial numbers, and locations.
2.  **Marine Corps Revenue** (FY2020–FY2024): Monthly and annual revenue data.
3.  **Navy Revenue** (FY2016–FY2024): Complex reports containing monthly summaries by location and reimbursement data.
4.  **District Revenues** (FY2020–FY2024): Aggregated revenue by district and base.
5.  **Financial Statements** (FY2020–FY2024): Balance sheets showing cash holdings, equity, and asset depreciation.
6.  **Revenue Comparison Reports** (FY2023–FY2024): Regional and branch comparisons.

**Data Dictionaries**
Detailed dictionaries are documented in `fa25-team-b/PDF Extraction/readme.md`. Key files include:
*   `Navy_Revenue_Reimburse_Summary.csv`: Installation-level annual revenue and NAFI reimbursements.
*   `Navy_Revenue_Report_FY20-FY24-2_monthly_summary_master.csv`: Granular monthly data (Location, Loc#, Month, Revenue).
*   `assets_by_region_service.csv`: Aggregated machine counts.

**What keywords or tags would you attach to the data set?**
*   **Domain:** Financial Data Analysis, Government Transparency, Public Policy.
*   **Tags:** Civic Tech, Gambling Addiction, Military Oversight, Budget Analysis.

---

## 3. Motivation & Composition

### Motivation
**For what purpose was the dataset created?**
> To address the lack of public transparency regarding gambling operations on US military bases. Despite generating **$70.9 million in net revenue in FY2024** alone, data was locked in opaque PDFs with inconsistent layouts, tiny fonts, and merged cells. This dataset enables oversight of potential gambling risks to service members.

### Composition
**What do the instances represent?**
> *   **Financial Records:** Monthly and annual revenue figures per base/machine.
> *   **Asset Records:** Individual slot machines (Manufacturer, Serial #, Installation Date).
> *   **Geospatial:** 79 overseas bases (Europe, Japan, Korea).

**Key Statistics:**
*   **Total Revenue (FY24):** $70.9 Million.
*   **Total Machines:** ~1,889.
*   **Geographic Split (Machines):** Europe (39.4%), Japan (37.8%), Korea (22.8%).

**Is the dataset a sample or complete?**
> It represents the complete set of records obtained via FOIA. However, **FY2024 data is partial** (annualized based on April YTD in some reports), and some specific data points (e.g., Yokosuka base) have quality issues due to source PDF corruption or tiny font sizes.

---

## 4. Collection Process & Technical Challenges

**How was the data collected?**
> MuckRock obtained PDFs via FOIA. The team used a variety of Python tools to handle the "human-readable" only format.

**Extraction Strategy by Document Type:**

| Report Type | Key Challenges | Tools & Solutions |
| :--- | :--- | :--- |
| **Asset Reports** | 8 different table layouts; COVID-specific categories in FY21. | `pdfplumber`, `pdftotext -layout`, `Camelot`. Custom parsers for each layout. |
| **Marine Revenue** | Misaligned columns; tables spanning multiple pages. | `pdfplumber` with custom page-by-page tunable tolerances. |
| **Navy Revenue** | **Extremely small fonts**; irregular "Monthly Summary by Location" tables. | `pdftotext -layout` combined with a **state-machine regex parser** to track line-by-line context. |
| **District Revenues** | Multi-line installation names. | `PyMuPDF` (coordinate-based extraction). |
| **Financial Stmts** | Large files, low scan quality. | `poppler-utils` split -> **Adobe Express OCR** -> Recombined. |

---

## 5. Preprocessing & Cleaning

**What cleaning was done?**
1.  **State Machine Parsing:** For Navy reports, used a state machine to detect installation blocks and propagate context (e.g., Base Name) to subsequent rows.
2.  **Dynamic Header Parsing:** Automatically detected fiscal year columns (e.g., discovering "FY16", "FY17" dynamically) rather than hard-coding.
3.  **Data Cleaning:**
    *   Standardized dashes/hyphens.
    *   Handled "Temp Closed" status to distinguish zero revenue from closures.
    *   Removed artifacts (e.g., "Oct 15" labels misread as text).
    *   **Outlier Removal:** Applied specific fixes for problem bases like Yokosuka and Souda Bay.
4.  **Consolidation:** Merged multi-block tables split across PDF pages into unified CSVs.

**Is the code available?**
> Yes. Extraction scripts are in `fa25-team-b/PDF Extraction/` and cleaning/EDA notebooks are in `fa25-team-b/eda/`.

---

## 6. Analysis & Uses

**Key Findings from Analysis:**
1.  **Top Revenue Generators:**
    *   **Camp Humphreys (Army, Korea)** is consistently a top earner (~$60.9M cumulative).
    *   **Camp Butler/Foster (USMC, Japan)** is the single highest-grossing location (~$70.6M cumulative).
    *   **Yokosuka (Navy, Japan)** leads Navy installations (~$36.5M cumulative).
2.  **Geographic Dominance:**
    *   **Army in Korea** generates ~$100.6M total (highest per-base average: ~$20.1M).
    *   **USMC & Navy** revenue is heavily concentrated in **Japan**.
3.  **Temporal Trends:**
    *   **COVID-19:** Sharp revenue decline in FY2020.
    *   **Recovery & Surge:** Steady recovery through FY2023.
    *   **FY2024 Pullback:** Revenue and machine counts showed a decline in FY2024 after the FY2023 peak.
4.  **Machine Inventory Anomaly:**
    *   Machine counts hit a low in FY2022, then **tripled in FY2023** (system-wide refresh), followed by a partial reduction in FY2024.

**Datasette Dashboard**
A public dashboard was built featuring:
*   **Installations Map:** Interactive filtering by branch/district.
*   **Revenue by Month:** Line charts showing seasonal trends and pandemic impact.
*   **Branch vs. District Heatmap:** Visualizing concentration of revenue.

**Potential Future Uses**
*   Policy research on military gambling regulations.
*   Health studies correlating base revenue with addiction rates.
*   Longitudinal tracking of vendor market share (IGT, Aristocrat, etc.).

---

## 7. Distribution & Maintenance

**Access Type**
> **External Open Access**.

**Maintenance**
> Codebase allows for reproducible extraction. Future contributors can add new fiscal year PDFs to the pipeline.

**Known Limitations**
*   **Navy Report Quality:** Tiny fonts in source PDFs caused persistent OCR challenges for Yokosuka base data.
*   **FY2024 Completeness:** FY24 figures in some reports are annualized based on partial year data (through April).
