
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

**FY2021 Asset Report**
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

### Setup Instructions

Before starting the notebook, ensure you have the correct Python environment configured.

**1. Open FY2021_Asset_Report_Extraction.ipynb**

**2. Install Required Dependencies**
```bash
pip install -r requirements.txt
```
**3. Run the notebook cells sequentially to extract and standardize tables.**

**4. Exported CSVs will appear in the output folder and are aligned for merging with other fiscal years.**

## 1.2. Marine Revenue

## 1.3. Navy Revenue Report

## 1.4. Financial Statements
The Financial Statements pdf required a bit of expirimentation for both OCR tools as well as formatted text extraction. Due to the size of the document, some extraction libraries and most online tools for OCR would not process the file. For text extraction, we ended up using poppler-utils, which had the best balance between quality of the table formatting during extraction alongside time to extract. For OCR, we initially tried using python libraries, but none worked particularly well or quickly. To solve this, we ended up splitting the document into chunks, running them through Adobe Express's OCR tool, then recombining them into one pdf. This was a successful approach, and the rest of the work done was in cleaning minor issues in extraction/formatting before loading data into our CSV files.
## 1.5. District Revenue

## 1.6. Revenue Comparison File
 
The Revenue Comparison file required a highly manual extraction process due to the complexity and inconsistency of the original document. Many pages contained multiple tables with varying formats, visual layouts, and informational elements that were not needed for the final dataset, making automated extraction unreliable.

To complete this extraction, **Adobe Express** was used extensively. **Pages 5–26, 30, 31, 46, and 58–79** of the original PDF were removed to isolate only the relevant content. Each remaining table was then extracted individually—often requiring multiple separate passes through **Adobe Express** due to differences in formatting and structure.

Once all related tables were successfully extracted, they were manually merged and organized into the Excel workbook, resulting in the final Revenue Comparison file. This workflow ensured that only the required tables were included while avoiding the noise introduced by unstructured visuals and non-uniform table layouts present throughout the document.
