
<h1 align="center">
  <br>
  <a href="https://www.bu.edu/spark/" target="_blank"><img src="https://www.bu.edu/spark/files/2023/08/logo.png" alt="BUSpark" width="200"></a>
</h1>



<p align="center">
  <a href="#key-features">Key Features</a> •
  <a href="#how-to-use">How To Use</a> •
  <a href="#project-description">Project Description</a> •
  <a href="#data-locations">Data Locations</a>
</p>

# MuckRock: US Military Base Slot Machine Revenue Explorer

## Overview

The Data Liberation Project, run by MuckRock, is an initiative to **identify, obtain, reformat, clean, document, publish, and disseminate government datasets of public interest**.

This repository contains the code, analyses, and documentation produced by **Team B** for the **Fall 2025 (FA25)** offering of Boston University's **DS 701: Tools for Data Science (Spark!)**. The goal of the course project is to assist the MuckRock team by investigating publicly available datasets, building tools to clean and analyze the data, and preparing documentation so that future volunteers can easily reproduce and extend the work.

---

## Project Description and Objectives

This project was assigned by the MuckRock Foundation in collaboration with BU Spark! to provide students with hands-on experience in data acquisition, cleaning, and analysis for public good.

The Team B mission in FA25 is to:

1. Extracted all the data from PDF files provided by MuckRock to csv files.

2. Perform exploratory analysis to understand the structure, completeness, and potential insights in the data.

3. Build repeatable python scripts to clean and harmonize the data for downstream use.

4. Document the dataset thoroughly using GitHub.

5. Create a Datasette user interface for the future users to work on it. With the features such as: SQL query, chart, dashboard, map...etc. 

6. Summarize findings and deliver an organized codebase that future teams can build upon.

7. Answer base questions.

- 1. What is the total and per‑base slot machine revenue by military branch and by region?
Below is the total slot machine revenue by military branch and by region

| Military Branch | Region | # Bases | Total Slot Revenue | Per‑Base Slot Revenue |
| --------------- | ------ | ------- | ------------------ | --------------------- |
| Army            | Europe | 12      | $56,722,390        | $4,726,866            |
| Army            | Japan  | 2       | $6,701,208         | $3,350,604            |
| Army            | Korea  | 5       | $100,568,956       | $20,113,791           |
| Navy            | Europe | 4       | $11,521,089        | $2,880,272            |
| Navy            | Japan  | 6       | $41,435,211        | $6,905,868            |
| Navy            | Korea  | 1       | $1,599,465         | $1,599,465            |
| USMC            | Japan  | 7       | $58,054,966        | $8,293,567            |



<img width="3553" height="1753" alt="total_revenue_by_region_and_service" src="https://github.com/user-attachments/assets/badd35ab-372e-4b42-9fad-39961f100f66" />

This compares the total slot‑machine revenue for the Army (blue), Marine Corps (orange) and Navy (green) across three regions: Korea, Japan and Europe. The y‑axis measures total revenue in millions of U.S. dollars. Key observations include:

Army in Korea: five Army bases in Korea generate roughly $100 million, dwarfing all other branch/region combinations and making the Army in Korea the largest revenue driver.
Japan: Marine Corps and Navy activities in Japan bring in around $58 million and $41 million respectively, while the Army’s two bases there contribute a modest $7 million.
Europe: the Army’s 12 bases collect about $57 million, and Navy bases about $15 million; the Marine Corps does not operate slot machines in Europe.
The call‑outs on the right summarise these points: the Army in Korea is the biggest contributor, and Marine Corps slot‑machine revenue is confined to Japan.

<img width="3553" height="1753" alt="top10_bases_total_revenue" src="https://github.com/user-attachments/assets/5b23a6fe-aeab-4104-9b60-3f9b3f2372af" />

The second slide ranks the top 10 individual bases by total slot‑machine revenue. The bases are colour‑coded by service branch (blue = Army, orange = Marine Corps, green = Navy). Notable findings:

Camp Humphreys (Army) is the single highest‑earning base at over $50 million.
Camp Butler / Foster (Marine Corps) follows at about $41 million.
Other high‑earning Army bases include AFRC Dragon Hill Lodge, Kaiserslautern, Wiesbaden, Daegu, Casey/Hovey and Stuttgart, each ranging from roughly $10 million to $22 million.
The Navy’s major contributor in this list is Yokosuka (around $21 million), and the Marine Corps’ Iwakuni base rounds out the top ten at about $10 million.
Annotations emphasize that seven out of the ten top‑earning bases belong to the Army and that revenue is heavily concentrated among a few installations.

- 2. Which bases generate the highest total revenue, and how does that rank change by year and by branch?
- 3. Which types of games or machines generate the most revenue? (CANT ANSWER RIGHT NOW)
- 4. How have the types of games or machines installed at bases changed over time? (CANT ANSWER RIGHT NOW)

---
 ## Datasette UI Showcase

 [![Demo Video](Datasette%20Demo%20shortcut.jpg)](https://drive.google.com/file/d/1pSkng9Hb7rHxbLF-UwirTGY_oIMbWXiH/view?usp=sharing)

---

## Data

This project focuses on liberating and structuring several key ARMP datasets, including slot machine 
- Asset Reports (FY2020, FY2021, FY2022, FY2023, FY2024)
- Marine revenue
- Navy revenue
- District revenues
- Financial Statement
- Revenue Comparison

These cleaned tables power downstream analysis and public-facing tools like Datasette.
For a detailed, table-by-table description of our extraction pipelines and outputs, see fa25-team-b-dev/PDF Extraction/readme.md,
which documents the asset, marine, navy, district revenue, and revenue comparison workflows.

## Repository Structure

The repository is organized to make it easy for others to pick up where this team leaves off. Below is a high–level description of the actual structure. If any folders or files mentioned below are missing or renamed in your local copy, please update this README accordingly.

| Path (relative to repo root)                            | Purpose                                                                                                                                                        |
| -------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `fa25-team-b-dev/fa25-team-b/`                          | All work for the FA25 Team B development effort. Inside this folder you should find notebooks, scripts, and data used for our analyses.                       |
| `fa25-team-b-dev/fa25-team-b/eda/`                      | Early explorations and exploratory data analysis (EDA). Each notebook should have a descriptive filename and include clear markdown explaining its purpose.   |
| `fa25-team-b-dev/fa25-team-b/PDF Extraction/`           | Python scripts and notebooks for cleaning and processing data from PDF files into CSV files (e.g., Asset, Marine, Navy, District, Revenue Comparison, etc.). |

## Where to start / Key notebooks

If you’re new to this repo and just want to understand what we did, start here:

#### 1. Early insights & EDA

If you want to see **early insights and sanity checks on the extracted data** (distributions, basic trends, data quality):

- `fa25-team-b-dev/fa25-team-b/eda/<THE_EDA_YOUWANT>.ipynb`  
  – High-level exploratory analysis on the cleaned revenue tables (e.g. summary stats by base, fiscal year, branch).


#### 2. PDF → CSV extraction pipelines

If you want to understand **how raw PDFs are turned into structured CSVs**：

- `fa25-team-b-dev/fa25-team-b/PDF Extraction/FY2021_Asset_Report_Extraction.ipynb`  
  – End-to-end extraction of the FY2021 Asset Report into standardized tables (summary + detail CSVs, with cleaning and column standardization).

- `fa25-team-b-dev/fa25-team-b/PDF Extraction/Marine_Revenue_FY20_FY24.ipynb`  
  – Extracts and cleans the Marine revenue report (FY20–FY24) into CSVs capturing game counts, handle, revenue, and per-base metrics.

- `fa25-team-b-dev/fa25-team-b/PDF Extraction/District_Revenues_FY20_FY24.ipynb`  
  – PyMuPDF-based extraction for the District Revenues FY20–FY24 PDF, including logic to handle multi-line rows and header parsing.


#### 3. Detailed dataset documentation

For **details, extraction logic, and data dictionaries**, please refer to:

- `fa25-team-b-dev/fa25-team-b/PDF Extraction/README.md`  
  – Describes what each PDF source contains, how we parsed it (e.g. `pdftotext`, `pdfplumber`, `PyMuPDF`), what CSVs are produced, and what each column means.

---

## Environment Setup

To reproduce the analyses or run the code yourself, follow these steps. Replace any placeholders with the actual commands or file names once they are finalized.

### 1. Clone the repository

```bash
git clone <repository_url>
cd MuckRock_project
```

### 2. Create a virtual environment

We recommend using either conda or Python’s built-in venv to manage dependencies.

Using conda:

```bash
conda create -n muckrock-fa2025 python=3.10
conda activate muckrock-fa2025
```

Using venv (alternative):

```bash
python -m venv .venv
source .venv/bin/activate   # on macOS/Linux
# .venv\Scripts\activate    # on Windows
```


### 3. Install dependencies

A requirements.txt or environment.yml file should list all Python packages needed to run the scripts and notebooks. If this file does not yet exist, please generate one by exporting your environment or writing down the packages you installed.

```bash
# via requirements.txt (update the filename/path if different)
pip install -r ds-muckrock-liberation/fa25-team-b-dev/PDF Extraction/requirements.txt
```

### 4. Configure data paths

Some notebooks may reference data stored on Google Drive. Before running those notebooks, make sure you have access to the data and update any hard-coded file paths.

You may provide a .env.example file to illustrate how to supply secrets (such as API keys) without committing them to Git. Users can then copy it to .env and fill in their own values.


Drive link: https://drive.google.com/drive/folders/1CZ0JF2y9IhaPy-KH4tkH2YbJyr750urc?usp=drive_link


### 5. Run notebooks and scripts

Use JupyterLab, VS Code, or your preferred IDE to explore the notebooks in the notebooks/ folder.

Best practices:

Clear all outputs before committing changes.

Ensure each notebook runs top-to-bottom without errors.

If a notebook is meant to be run as a script, indicate that clearly at the top in markdown.

### 6. Contributing workflow

All development should occur on branches off of dev (or the main development branch specified by your PM/TPM). After making changes:

Commit and push your branch:
```bash
git add .
git commit -m "Describe your change"
git push origin <your-branch-name>
```

Then:

Open a Pull Request targeting the dev branch.

Request reviews from your PM/TPM.

Open a final Pull Request from dev to main.
