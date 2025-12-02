# Project Datasheet: MuckRock US Military Base Slot Machine Revenue Explorer

## 1. Project Information

**What is the project name?**
> **MuckRock: US Military Base Slot Machine Revenue Explorer**

**What is the link to your project's GitHub repository?**
> *https://github.com/BU-Spark/ds-muckrock-liberation/tree/fa25-team-b-dev/fa25-team-b*

**What is the link to your project's Google Drive folder?**
> [Spark! Owned Google Drive Folder](https://drive.google.com/drive/folders/1CZ0JF2y9IhaPy-KH4tkH2YbJyr750urc?usp=drive_link)

**In your own words, what is this project about? What is the goal of this project?**
> This project focuses on liberating and analyzing data from the **Army Recreation Machine Program (ARMP)**, which operates slot machines on overseas U.S. military bases.
>
> **Goal:** To extract, clean, and structure financial and operational data from unstructured PDF documents to enable transparency into slot machine revenue distribution across bases, branches, and regions.
>
> **Impact:** The project aims to support public understanding of gambling risks faced by service members, identify patterns in revenue trends, and provide accessible tools (such as a Datasette interface) for policymakers and researchers.

**Who is the client for the project?**
> **MuckRock Foundation**

**Who are the client contacts for the project?**
> *[To be filled by project team - client contact information]*

**What class was this project part of?**
> **DS 701: Tools for Data Science (Spark!) - Fall 2025 (FA25), Boston University**

---

## 2. Dataset Information

**What data sets did you use in your project?**
The project uses multiple datasets extracted from PDF documents provided by MuckRock. All datasets are stored in the [Project Google Drive](https://drive.google.com/drive/folders/1CZ0JF2y9IhaPy-KH4tkH2YbJyr750urc?usp=drive_link).

1.  **Asset Reports** (FY2020–FY2024): Slot machine inventory, manufacturers, locations, and status.
2.  **Marine Revenue Reports** (FY2020–FY2024): Monthly and annual revenue for Marine Corps installations.
3.  **Navy Revenue Reports** (FY2016–FY2024): Revenue and reimbursement data by country/installation.
4.  **District Revenues** (FY2020–FY2024): Aggregated revenue by district, base, and location (all branches).
5.  **Financial Statements**: Overall financial health (cash holdings, equity, depreciation).
6.  **Revenue Comparison Reports** (FY2023–FY2024): Comparative data across regions and branches.

**Data Dictionaries**
Detailed dictionaries are in: `fa25-team-b/PDF Extraction/readme.md`.

*   **Asset Reports:**
    *   `assets_by_region_service.csv`: Region, Service, Asset counts, EGM counts.
    *   `assets_by_field_office.csv`: Field Office stats.
    *   `installed_assets_location_manufacture.csv`: Manufacturer & Service Type details.
    *   `asset_details.csv`: Serial numbers, Acquisition dates, Asset types.
    *   `floor_asset_details.csv` & `floor_summary_details.csv`: Site/Floor metadata.
    *   `site_operational_status.csv`: Operational status.
    *   `years_in_storage.csv`: Asset age info.

*   **Marine Revenue:**
    *   `Marine_Revenue_FY20-FY24_summary table.csv`: Country/Installation summaries.
    *   `Marine_Revenue_FY20-FY24_detail.csv`: Detailed monthly revenue.

*   **Navy Revenue:**
    *   `Navy_Revenue_Report_monthly_summary.csv`: Installation, Country, Month, Year, Revenue.

*   **District Revenue:**
    *   `District_Revenue_filtered_FY20-FY24_final.csv`: Service, Category, Region, Base, Month, Year, Amount.

**What keywords or tags would you attach to the data set?**
*   **Domain:** Other (Financial Data Analysis, Government Transparency, Public Policy Analysis)
*   **Tags:** Civic Tech, Budget, Health (gambling addiction), Policing (military oversight)

---

## 3. Motivation & Composition

### Motivation
**For what purpose was the dataset created?**
> The original PDFs were for internal ARMP financial reporting. MuckRock obtained them via FOIA to address a transparency gap.
>
> **Gap Filled:** While military slots generate millions, public data was non-existent. This dataset converts unstructured PDFs into structured formats to enable public oversight, policy analysis, and research into gambling-related harms.

### Composition
**What do the instances represent?**
The format is primarily **tabular data (CSV)** extracted from multimodal PDF sources.
1.  **Financial Records:** Transactions, monthly revenue, financial statement entries (Time series: FY2016–2024).
2.  **Asset Records:** Individual slot machines, manufacturers, locations, status (Geospatial attributes).
3.  **Aggregate Summaries:** Statistics by base, region, or branch.

**How many instances are there?**
*   **Asset Records:** ~1,889 operational machines (FY2024).
*   **Revenue Records:** Thousands of monthly records across District, Marine, and Navy reports.
*   **Locations:** 79 overseas military bases (Europe: 39.4%, Japan: 37.8%, Korea: 22.8% of machines).

**Is the dataset a sample or complete?**
> It represents the **complete set of available records obtained through FOIA**.
> *Limitations:* FY2024 may be incomplete; some data lost due to OCR errors or PDF damage (e.g., Yokosuka base); domestic bases are excluded.

**What data does each instance consist of?**
> **Cleaned and structured features.**
> *   *Example Revenue:* Service, Region, Base, Month, Year, Cleaned Amount.
> *   *Example Asset:* Manufacturer, Serial #, Installation Date, Location, Status.

**Is there missing information?**
> Yes, due to:
> 1.  **Extraction Errors:** OCR failures, complex layouts, damaged PDFs (notably Japan bases).
> 2.  **Source Issues:** Blank cells in original PDFs.
> 3.  **Scope:** Incomplete fiscal years.

**Are there recommended data splits?**
> **No.** This is not a machine learning dataset.
> *Natural Organization:* By Fiscal Year, Service Branch, or Region.

**Are there errors or noise?**
> Yes. Sources include OCR misreads ("0" vs "O"), table parsing errors, inconsistent base naming ("Camp Butler" vs "Camp Butler/Foster"), and currency formatting issues.

**Privacy & Ethics**
*   **Confidentiality:** No PII. Only aggregate financial/operational data.
*   **Sensitive Content:** Financial data is neutral, but the context (gambling) relates to addiction/health.
*   **Identification:** No individuals can be identified.

---

## 4. Dataset Snapshot

**Asset Reports Dataset**
| Metric | Description |
| :--- | :--- |
| **Number of instances** | ~1,889 machines (FY2024), plus historical (FY20-24) |
| **Number of fields** | 8-15 fields (Region, Service, Manufacturer, Serial #, etc.) |
| **Labels** | Branch (Army, Navy...), Region (Europe, Japan...), Vendor (IGT, BAL...) |

**Revenue Datasets (District, Marine, Navy)**
| Metric | Description |
| :--- | :--- |
| **Number of instances** | Thousands of monthly records |
| **Number of fields** | 6-8 fields (Service, Region, Base, Month, Year, Amount) |
| **Labels** | Service Branch, Region, Revenue Category |

**Financial Statements Dataset**
| Metric | Description |
| :--- | :--- |
| **Number of instances** | Monthly/quarterly snapshots (FY20-24) |
| **Number of fields** | 10+ (Cash, Equity, Asset Values, Liabilities) |

---

## 5. Collection Process

**How was the data collected?**
> **Source:** Provided by MuckRock via **FOIA requests** to the DOD/ARMP.
> **Process:**
> 1. MuckRock received PDFs from the government.
> 2. Project team extracted data using Python (`pdfplumber`, `PyMuPDF`, `Camelot`, etc.).
> 3. Validation via cross-referencing totals (e.g., FY24 total $70.9M).

**Timeframe**
*   **Collection:** Fall 2025.
*   **Data Coverage:** FY2016 – FY2024.

---

## 6. Preprocessing & Cleaning

**What cleaning was done?**
1.  **Currency:** Removed symbols ($, commas), fixed negative values `()`.
2.  **Dates:** Standardized to `YYYY-MM`.
3.  **Text:** Cleaned base names, handled merged cells.
4.  **Handling Missing/Bad Data:** Filled NaNs with 0.0 (financial), removed corrupt rows (e.g., problematic Japan bases), removed outliers (IQR method).
5.  **Structure:** Rebuilt multi-page tables and fixed column alignment.

**Is the raw data saved?**
> Yes. Raw PDFs are in the Google Drive. Extraction code can reproduce CSVs.

**Is the code available?**
> Yes. See `fa25-team-b/PDF Extraction/` for extraction scripts and `fa25-team-b/eda/` for cleaning/analysis notebooks.

---

## 7. Uses

**What has the dataset been used for?**
*   **EDA:** Analysis of revenue patterns, geographic distribution, and financial health.
*   **Answering Questions:** Identifying highest-revenue bases (Army/Korea dominance) and vendor changes.
*   **Visualization:** Charts of revenue trends and inventory.
*   **Tools:** Development of a **Datasette** interface for public querying.

**Potential Future Uses**
*   Longitudinal trend analysis & Risk assessment research.
*   Comparisons across branches/regions.
*   Policy impact studies (e.g., effect of COVID-19).
*   Vendor market share analysis.

**Tasks NOT recommended**
*   Individual identification (impossible).
*   Real-time monitoring (data is historical).
*   Definitive causal inference (lacks experimental controls).

---

## 8. Distribution & Maintenance

**Access Type**
> **External Open Access** (Public transparency).

**Maintenance / Contribution**
> *   **Mechanism:** GitHub Repository (Pull Requests).
> *   **Reproducibility:** Extraction pipeline allows re-processing or adding new fiscal years.
> *   **Documentation:** Refer to `PDF Extraction/readme.md`.

---

## 9. Additional Notes

1.  **Scale:** As of FY2024, ARMP operates **1,889 machines** across **79 bases**, generating **$70.9M**.
2.  **Key Insight:** Asia-Pacific (Japan + Korea) accounts for >70% of total revenue.
3.  **Tech Stack:** `pdfplumber`, `PyMuPDF`, `pdftotext`, `Camelot`, `Tabula`.
4.  **Known Issues:** Yokosuka, Sasebo, Souda Bay, and Atsugi bases have data quality issues requiring manual attention.
