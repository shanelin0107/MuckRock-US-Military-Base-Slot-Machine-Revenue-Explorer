
<h1 align="center">
  <br>
  <a href="https://www.bu.edu/spark/" target="_blank"><img src="https://www.bu.edu/spark/files/2023/08/logo.png" alt="BUSpark" width="200"></a>
  <br>
  Project README Template <change to project name>
  <br>
</h1>

<h4 align="center">A template for the project readme file. </h4> <change to repo short description>

# 1. Detailed Data Extraction Procedure


## 1.1. Asset Report

### FY2020, FY2023, FY2024 Asset Report
The Asset Reports are distributed as complex, multi-layout PDF files containing both summary and detailed operational tables. Each report includes sections such as **Region Summaries**, **Field Office Statistics**, **Installed Asset Details**, and **Operational Status Reports**. Because each section follows a distinct text layout, this pipeline implements **dedicated parsing functions** for each format and automates their extraction into **eight standardized, analysis-ready CSV outputs per fiscal year** for downstream analytics and visualization.

| Output CSV                         | Description                                                                 |
|------------------------------------|------------------------------------------------------------------------------|
| `assets_by_region_service.csv`     | Summary of assets by region and service (Army, Navy, Air Force, etc.)        |
| `assets_by_field_office.csv`       | Asset and EGM counts by field office                                         |
| `installed_assets_location_manufacture.csv` | Installed assets by manufacturer and service type                  |
| `asset_details.csv`                | Detailed list of individual assets, including serial numbers, acquisition dates, and types |
| `floor_asset_details.csv`          | Floor-level installation details for each site                               |
| `floor_summary_details.csv`        | Floor summary metadata and occupancy information                             |
| `site_operational_status.csv`      | Site operational status and service affiliation                              |
| `years_in_storage.csv`             | Pivot summary showing asset age versus years in storage                      |

#### Workflow Overview

1. **PDF Parsing and Month Detection**  
   The pipeline first uses `pdftotext -layout` to convert each page into structured text while preserving column alignment.  
   The `detect_month_map()` function then scans pages and assigns each one to its reporting month (e.g., *March 2024*).

2. **Section Identification and Parsing**  
   Each page is scanned for key headers such as `"Assets by Region, Service"`, `"Assets by Field Office"`, and `"Installed Assets by Location"`.  
   Based on these headers, specialized parsing functions are applied to extract the corresponding tables.  
   Extracted rows are validated, cleaned, and merged using `_safe_concat()`.

3. **Data Assembly and Export**  
   All parsed DataFrames are combined and exported into **eight standardized CSV files per fiscal year**, each stored in an automatically created output folder (e.g., `/content/FY2023_Asset_Report_output/`).


#### Key Features

- *Robust Layout Parsing* — Preserves table structure using `pdftotext -layout`.  
- *Automatic Month Mapping* — Identifies and links each page to its reporting month.  
- *Multi-Section Extraction* — Supports region, field office, installed asset, and detailed record tables.  
- *Error-Tolerant Processing* — Safely merges partial data and skips malformed rows.

#### Function Summary

Because the report contains **eight distinct table layouts**, we implement separate functions to handle each layout. Details:

| Function | Purpose |
|-----------|----------|
| `read_pdf_text_layout()` | Converts a PDF page layout into raw text. |
| `parse_region_and_field_office_v1()` | Extracts Region and Field Office summaries. |
| `parse_installed_assets_v2()` | Extracts Installed Assets by Location. |
| `extract_region_field_installed_v2()` | Orchestrates summary-level extraction for regions, field offices, and installed assets. |
| `parse_asset_details_page()` | Extracts detailed asset listings. |
| `parse_floor_details_page()` | Extracts floor-level installation data. |
| `parse_site_status_page()` | Extracts site operational status. |
| `extract_detailed_tables()` | Combines all detailed tables and applies month mapping. |
| `save_outputs()` | Writes all resulting DataFrames to CSV files. |
| `run_extraction()` | High-level orchestration for processing a single PDF file. |

### FY2021 Asset Report
The FY2021 Asset Report data has been fully extracted and cleaned for analysis. Unlike FY2020, FY2022, and FY2023, the FY2021 report contains several COVID-specific cells and temporary reporting categories, which required custom parsing and structural normalization during extraction.

The extraction notebook generates the following tables:
- Assets by Region, Service
- Assets by Field Office
- Installed Assets by Location & Manufacturer
- Asset Details (blue header)
- Floor Asset Details
- Site Operational Status
- Years in Storage

Data was parsed from the PDF using Camelot and Tabula, then cleaned with Pandas. Irregular headers, merged cells, and COVID-specific fields were standardized to match extract formats from other fiscal years.

**Setup Instructions** 

Before starting the notebook, ensure you have the correct Python environment configured.

*1. Open FY2021_Asset_Report_Extraction.ipynb*

*2. Install Required Dependencies*
```bash
pip install -r requirements.txt
```
*3. Run the notebook cells sequentially to extract and standardize tables.*

*4. Exported CSVs will appear in the output folder and are aligned for merging with other fiscal years.*

## 1.2. Marine Revenue
`Marine_Revenue_FY20_FY24.ipynb` uses **`pdfplumber`** to extract structured tables from the **Marine_Revenue_FY20–FY24.pdf** report into clean CSV files for downstream analysis or upload to Datasette. The notebook automates the end-to-end process of parsing,  Its main workflow includes:

-  **Table Extraction**: Automatically detects and extracts table structures page by page.

-  **Data Cleaning & Alignment**: Fixes common OCR and layout issues such as misaligned columns, inconsistent spacing, and merged rows.

-  **Output Generation**: Produces a detailed CSV where each row corresponds to a standardized, structured data record.

>  **Default Output Columns:**

>  `Loc #`, `Location`, `Month`, `Revenue`, `NAFI Amt`, `Annual Revenue`, `Annual NAFI`


### Functional Features

-  **Adjustable Extraction Parameters**

Fine-tune thresholds like `BASE_Y_TOL`, `BASE_X_JOIN`, and `BASE_GAP_RATIO` to handle varying table layouts and line spacing. Apply subtle left-shifts (e.g., `BASE_LEFT_SHIFT_MONTH`, `BASE_LEFT_SHIFT_REVENUE`) to align misparsed text into the correct columns.
| Parameter | Description |
|------------|-------------|
| `BASE_Y_TOL` | Vertical merge tolerance for row alignment |
| `BASE_X_JOIN` | Horizontal character join tolerance |
| `BASE_GAP_RATIO` | Whitespace threshold for smart joins |
| `BASE_EDGE_PAD` | Extra padding around column cut lines |
| `BASE_LEFT_SHIFT_MONTH` / `BASE_LEFT_SHIFT_REVENUE` | Pixel-level left correction for specific columns |
| `BASE_DROP_MIN` | Minimum number of non-empty columns to keep a row |

 
-  **Page-Specific Overrides**

To handle problematic pages, use the `SPECIAL_PARAMS` dictionary to define custom parameter sets for individual pages that deviate from the standard layout.
  

-  **Clean Filtering & Validation**

Automatically removes rows with too few non-empty fields (`BASE_DROP_MIN`) to maintain data integrity and prevent inclusion of noise.

### Output Description
**File name:** 
`Marine_Revenue_FY20-FY24_summary table.csv`
| Column              | Description                                                  |
| -------------------- | ------------------------------------------------------------ |
| `Page`              | Actual page number from the PDF (1-based)                    |
| `Country`           | Country name (normalized, e.g., `Japan`, `Korea`)            |
| `Installation`      | Installation name (normalized, e.g., `Camp Fuji`, `Iwakuni`) |
| `FY16`              | Monetary value converted to numeric (`$`, `,`, `( )` handled) |
| `FY17`              | Same as above                                                |
| `FY18`              | Same as above                                                |
| `FY19`              | Same as above                                                |
| `FY20 thru SEP`     | Same as above                                                |
| `Annualized FY20`   | Same as above                                                |
   
 `Marine_Revenue_FY20-FY24_detail.csv`
| Column | Description |
|---------|-------------|
| `Loc #` | Location ID |
| `Location` | Facility/installation name |
| `Month` | Month label (can later be standardized to numeric month) |
| `Revenue` | Monthly revenue |
| `NAFI Amt` | NAFI amount |
| `Annual Revenue` | Year-to-date total revenue |
| `Annual NAFI` | Year-to-date total NAFI |

## 1.3. Navy Revenue Report
We divided the Navy revenue report into two parts. The first part is the revenue and reimbursement summary, which aggregates installation-level revenue by country from FY16 to FY24. The second part is the Navy_Revenue_Report_monthly_summary.csv, a detailed monthly breakdown derived from the summary data that captures installation-level trends and temporal fluctuations across fiscal years.

Our methodology was to first convert the PDF to text using pdftotext -layout so that the original column alignment was mostly preserved on each line. We then used several regex patterns to detect section headers, month strings, Loc#, 6-digit site codes, and numeric amount fields. Next, we processed the file line by line and used a “state machine” approach to keep track of which installation or location the parser was currently in; when a line containing a month was found, we assembled it into a complete record and loaded it into pandas to produce the final CSV. Finally, we applied project-specific cleanup rules to drop corrupted rows for certain Japan bases—particularly Yokosuka, Souda Bay, Sasebo, and Atsugi. For Yokosuka especially, the extremely small font and damaged numeric fields still cause extraction issues, which we have already raised in the client meeting.

Additional development work focused on standardizing the Navy Revenue extraction pipeline. The updated script introduced dynamic fiscal-year detection, automated multi-line table alignment, and error-handling logic to manage incomplete or irregular records. These enhancements ensured that the extraction process remained consistent across both FY20–FY24-1 and FY20–FY24-2 reports.

## 1.4. Financial Statements
The Financial Statements pdf required a bit of expirimentation for both OCR tools as well as formatted text extraction. Due to the size of the document, some extraction libraries and most online tools for OCR would not process the file. For text extraction, we ended up using poppler-utils, which had the best balance between quality of the table formatting during extraction alongside time to extract. For OCR, we initially tried using python libraries, but none worked particularly well or quickly. To solve this, we ended up splitting the document into chunks, running them through Adobe Express's OCR tool, then recombining them into one pdf. This was a successful approach, and the rest of the work done was in cleaning minor issues in extraction/formatting before loading data into our CSV files.
## 1.5. District Revenue
This module focuses on parsing and structuring revenue data from the **_District Revenues FY20–FY24.pdf_** document, one of the most complex ARMP source files due to its inconsistent table layouts and mixed fiscal formats across pages.

### Extraction Summary
Data were extracted using **[PyMuPDF (`fitz`)](https://pymupdf.readthedocs.io/en/latest/)** to precisely capture text positions and reconstruct multi-page tables.

Key parsing logic includes:
- **Coordinate-based region filtering** : restricted to pages where the layout contains fiscal-year headers (FY20–FY24) and monetary values aligned in consistent columns.  
- **Regex pattern matching** : isolates *Country / Installation* blocks and detects table breaks between regions.  
- **Dynamic page filtering** : only pages with revenue tables (excluding summary or memo text) were processed to reduce noise.  
- **Normalization pipeline** : cleans monetary fields (`$, commas, spaces`), unifies fiscal-year columns, and merges split multi-line installation names.

### Output & Structure
The resulting CSV follows this schema:

| Column | Description |
|:--|:--|
| `Service` | Military branch (Army, Navy, Marine Corps) |
| `Category` | Revenue or Reimbursement |
| `Region` | Region label extracted from header |
| `Base` | Base name |
| `Location` | Facility name |
| `Month` | Month label |
| `Year` | Fiscal Year label |
| `Amount` | Monthly Revenue figures (USD) |

### Reproducibility
Run the following notebook to reproduce extraction:
```bash
PDF Extraction/District_Revenues_FY20_FY24.ipynb
```
Steps performed:
1. Mount Google Drive (if running in Colab).
2. Load the raw PDF from /content/drive/MyDrive/District Revenues FY20–FY24.pdf.
3. Apply PyMuPDF-based text-block filtering.
4. Save the structured CSV to /content/drive/MyDrive/District_Revenue_filtered_FY20-FY24_final.csv.

## 1.6. Revenue Comparison File
 
The Revenue Comparison file required a highly manual extraction process due to the complexity and inconsistency of the original document. Many pages contained multiple tables with varying formats, visual layouts, and informational elements that were not needed for the final dataset, making automated extraction unreliable.

To complete this extraction, **Adobe Express** was used extensively. **Pages 5–26, 30, 31, 46, and 58–79** of the original PDF were removed to isolate only the relevant content. Each remaining table was then extracted individually—often requiring multiple separate passes through **Adobe Express** due to differences in formatting and structure.

Once all related tables were successfully extracted, they were manually merged and organized into the Excel workbook, resulting in the final Revenue Comparison file. This workflow ensured that only the required tables were included while avoiding the noise introduced by unstructured visuals and non-uniform table layouts present throughout the document.
