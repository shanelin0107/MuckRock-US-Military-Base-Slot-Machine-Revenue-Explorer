<h1 align="center">
  <br>
  <a href="https://www.bu.edu/spark/" target="_blank"><img src="https://www.bu.edu/spark/files/2023/08/logo.png" alt="BUSpark" width="200"></a>
  <br>
  MuckRock: US Military Base Slot Machine Revenue Explorer
  <br>
</h1>

<h4 align="center">PDF Documents Archive</h4>

<p align="center">
  <a href="#overview">Overview</a> •
  <a href="#source--attribution">Source & Attribution</a> •
  <a href="#pdf-inventory">PDF Inventory</a> •
  <a href="#data-coverage">Data Coverage</a> •
  <a href="#how-to-use-these-pdfs">How to Use</a> •
  <a href="#data-quality--known-issues">Data Quality</a> •
  <a href="#notes-for-contributors">Contributing</a>
</p>

# Overview

This folder contains original PDF documents provided by **MuckRock** containing military base financial and operational data. These PDFs serve as the primary source documents from which structured CSV data is extracted for analysis and visualization.

The documents cover District Revenue, Asset Reports, and Service Branch-specific Revenue data for FY2020–FY2024.

For more details on how these PDFs are processed and extracted, refer to the [PDF Extraction folder](/fa25-team-b/%20PDF%20Extraction/readme.md).

---

# Source & Attribution

All PDF files in this folder are sourced from **[MuckRock](https://www.muckrock.com/)**, a nonprofit news organization that helps journalists, researchers, and citizens obtain and share government documents through Freedom of Information Act (FOIA) requests.

**Data Coverage**: FY2020–FY2024 (Fiscal Years)  
**Data Type**: Military Base Revenues, Asset Reports, and Financial Statements  
**Last Updated**: December 2024  
**FOIA Source**: U.S. Department of Defense

---

# PDF Inventory

## District Revenue Reports

Files containing district-level revenue data by base and service branch.

- **District_Revenues_FY20_FY24.pdf** (Primary source)
  - **Covers**: FY2020–FY2024
  - **Content**: District revenue breakdowns by military installation
  - **Extracted to**: `CSVs/District_Revenue/District_Revenue_filtered_FY20-FY24_final.csv`
  - **Status**: ✅ Processed and validated

## Asset Reports

Files containing asset valuations and inventory information for military installations.

- **FY2020_Asset_Report.pdf** | **FY2021_Asset_Report.pdf** | **FY2022_Asset_Report.pdf**
  - **Covers**: Fiscal years 2020–2022 respectively
  - **Content**: Asset inventory, valuations, and facility details by base
  - **Extracted to**: `CSVs/FY2020-2024_Asset_Report_Final/` (organized by fiscal year)
  - **Status**: ✅ Processed

- **FY2023_Asset_Report.pdf** | **FY2024_Asset_Report.pdf**
  - **Covers**: Fiscal years 2023–2024
  - **Content**: Updated asset information and property details
  - **Extracted to**: `CSVs/FY2020-2024_Asset_Report_Final/` (organized by fiscal year)
  - **Status**: ✅ Processed

## Revenue Reports by Service Branch

### Marine Revenue

- **Marine_Revenue_FY20_FY24.pdf**
  - **Covers**: FY2020–FY2024
  - **Content**: Marine Corps slot machine and MWR revenue by installation
  - **Extracted to**: `CSVs/Marine_Revenue/Marine_Revenue_FY20-FY24_detail_with_gps.csv`
  - **Status**: ✅ Processed

### Navy Revenue

- **Navy_Revenue_Report_1.pdf** | **Navy_Revenue_Report_2.pdf**
  - **Covers**: FY2020–FY2024 (combined)
  - **Content**: Navy base revenue streams including NAFI and slot machine revenue
  - **Extracted to**: `CSVs/Navy_Revenue/` (split by fiscal year or region)
  - **Status**: ✅ Processed

## Financial Statements

- **Financial Statements.pdf**
  - **Covers**: Multi-year consolidated financial summaries
  - **Extracted to**: `CSVs/Financial_Statements/`
  - **Status**: Check extraction status

---

# Data Coverage

| Fiscal Year | District Revenue | Asset Reports | Marine Revenue | Navy Revenue |
|---|---|---|---|---|
| FY2020 | ✅ | ✅ | ✅ | ✅ |
| FY2021 | ✅ | ✅ | ✅ | ✅ |
| FY2022 | ✅ | ✅ | ✅ | ✅ |
| FY2023 | ✅ | ✅ | ✅ | ✅ |
| FY2024 | ✅ (Partial) | ✅ (Partial) | ✅ (Partial) | ✅ (Partial) |

---

# How to Use These PDFs

## For Data Extraction

1. Use Python scripts in the `PDF_Extraction/` folder to parse and extract data from PDFs
2. Output CSV files should be saved to the corresponding folder in `CSVs/`
3. Refer to `PDF_Extraction/readme.md` for specific script-to-PDF mappings and instructions

## For Reference & Validation

1. Open PDFs to verify extracted data accuracy
2. Cross-reference specific tables, figures, or numbers with CSV outputs
3. Check for any data discrepancies or missing sections

## For New Analysis

1. Identify the PDF(s) relevant to your research question
2. Check `CSVs/` folder to see if extraction is already complete
3. If extraction is incomplete, refer to extraction scripts and create new outputs
4. Document any data issues in the corresponding CSV README or GitHub issue

---

# Data Quality & Known Issues

## General Notes

- PDFs may contain scanned images (OCR) or native text; OCR accuracy may vary
- Some tables span multiple pages; extraction scripts handle pagination
- Fiscal year definitions follow U.S. military fiscal calendar (October–September)
- Base names may appear with slight variations; refer to `CSVs/bases.csv` for standardized identifiers

## FY2024 Data

- Some reports contain only partial FY2024 data (not full 12 months)
- Use with caution in year-over-year trend analysis
- Complete data expected in updated releases

## Base Name Inconsistencies

- Base names may have spelling variations across different PDFs (e.g., "Camp Hanson" vs "Camp Hansen")
- Refer to `CSVs/bases.csv` for standardized base identifiers
- Check extraction scripts for name normalization rules

## Missing or Redacted Data

- Some entries may be redacted in original PDFs (represented as blank or "N/A" in extracted CSVs)
- Contact MuckRock or DoD for clarification on redacted sections

---

# Notes for Contributors

- **Do NOT modify original PDF files** in this folder; treat them as read-only archives
- If a new version of a PDF is obtained from MuckRock, save it with a date suffix (e.g., `District_Revenues_FY20_FY24_v2_Dec2024.pdf`)
- Update the extraction scripts if PDF structure or format changes
- Document any data quality issues or extraction challenges in GitHub issues or team communications
- Always attribute data to MuckRock in any reports, presentations, or publications

---

## Document References

- **MuckRock Project**: https://www.muckrock.com/
- **PDF Extraction**: See `PDF_Extraction/readme.md` for technical details
- **Extracted Data**: See `CSVs/README.md` for CSV file structure and fields
- **Analysis Examples**: See `Base_Question/` and `EDA/` for data usage examples

---

## Contact & Support

For questions about MuckRock data or FOIA requests, visit:
- **MuckRock Website**: https://www.muckrock.com/
- **MuckRock FAQ**: https://muckrock.com/faq/
- **Team Contact**: Refer to project README for team leads and contact information



