# 🎰 U.S. Military Base Slot Machine Revenue Explorer

An interactive Datasette deployment that surfaces FY2020–FY2024 slot machine revenue reported across U.S. military installations worldwide. This repo packages the cleaned FOIA dataset, a reproducible SQLite build pipeline, and the Docker/Render config required for push-button hosting.

## Key Figures
- **1,889** slot machines operate across morale, welfare & recreation facilities
- **79** global locations span Europe, the Pacific, and contingency sites
- **$70.9M** reported FY2024 revenue
- **Coverage:** FY2020 – FY2024 (fiscal calendar, Oct–Sep)

## 🌐 Live Demo
- Live Render URL: https://ds-701-muckrock-data-liberation-project.onrender.com

## Repository Structure
```
military-slots-explorer/
├── data/
│   └── District_Revenue_FY20-FY24_with_lat_lon_clean.csv
├── convert_csv_to_db.py
├── military_slots.db
├── requirements.txt
├── Dockerfile
├── metadata.yaml
├── render.yaml
├── DATA_DICTIONARY.md
├── README.md
└── .gitignore
```

## Local Development
1. **Clone the repo**
   ```powershell
   git clone <your-fork-url> military-slots-explorer
   cd military-slots-explorer
   ```
2. **Create & activate a virtual environment**
   ```powershell
   py -3.13 -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```
3. **Install dependencies**
   ```powershell
   pip install -r requirements.txt
   ```
4. **Regenerate the SQLite database (optional but recommended)**
   ```powershell
   python convert_csv_to_db.py
   ```
   This script:
   - Parses `data/District_Revenue_FY20-FY24_with_lat_lon_clean.csv`
   - Calculates fiscal years (Oct–Sep)
   - Normalizes column names and datatypes
   - Builds `military_slots.db` with helpful indexes
5. **Launch Datasette locally**
   ```powershell
   datasette military_slots.db -m metadata.yaml --cors
   ```
   Visit http://localhost:8001 to browse tables, preset queries, and plugins (cluster map + Vega charts). Stop with `Ctrl+C`.

## Deployment to Render
1. Push this repository to GitHub (set the remote to your repo, commit, and `git push`).
2. Log into [Render](https://render.com) with GitHub and create a new **Web Service**.
3. Render auto-detects `render.yaml` and the Docker build. Keep the **Free** instance type and leave build/start commands blank.
4. Once the dashboard shows **Service is live**, copy the public URL and update the **Live Demo** section in this README as well as the GitHub repo description/website fields.

## Core Features
- Rich metadata with default filters (branch, country, fiscal year, installation)
- Pre-built SQL queries highlighting branch totals, top installations, yearly trends, and geography splits
- Datasette Cluster Map plugin for instant geospatial exploration
- Datasette Vega plugin for on-the-fly charts
- Dockerfile tuned for Render's `$PORT` + CORS requirements

## Data Source
- **Primary:** Slot machine revenue disclosures obtained via MuckRock FOIA request (Army, Navy, Marine Corps)
- **Format:** Monthly revenue entries tagged with branch, facility, fiscal year, and geocoded coordinates
- **Processing:** Notebook parsing of PDF statements followed by the `convert_csv_to_db.py` pipeline described above

## Background Reading
- [WIRED — “The Military’s Slots Are Raking In Millions”](https://www.wired.com/story/military-slot-machines/)
- [GAO Report GAO-17-623 — “DoD’s Slot Machine Operations”](https://www.gao.gov/products/gao-17-623)
- [NPR — “U.S. Military’s $100 Million Slot Machine Habit”](https://www.npr.org/2015/05/19/407786744/u-s-militarys-100-million-slot-machine-habit)

## Project Team
- **BU Spark!** — project sponsor & delivery partner
- **MuckRock** — FOIA partner and data provider

## License & Attribution
- **Code:** MIT License (feel free to adapt with attribution)
- **Data:** Released for public research via MuckRock FOIA responses; cite MuckRock + DS 701 project team when publishing derivative work.
