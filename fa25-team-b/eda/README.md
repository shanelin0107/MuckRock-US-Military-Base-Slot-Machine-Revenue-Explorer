# Data - Marine revenue

## Data Cleaning Steps - Marine revenue

### 1. Columns Containing Numeric (Fiscal) Values
For columns that contain fiscal or monetary numbers, the following cleaning steps are applied:

- Convert each value to a string and strip leading/trailing whitespace.  
- Use regular expressions to remove non-numeric symbols** such as `$`, commas, and other special characters.  
- Convert the cleaned string to a floating-point number (`float`).  
- Detect and handle parentheses indicating negative values — e.g., `(1,200)` → `-1200.0`.  
- Replace missing or unparsable values with `0.0`.


### 2. Columns Containing Month or Date Information
For columns representing months or dates, the following cleaning logic is used:

- Normalize valid month strings into a standardized `YYYY-MM` format.  
- Let pandas automatically infer the date format and return the value in `YYYY-MM-DD` format.  
- If all parsing attempts fail, return an empty string.

---


## Visualization Findings - Marine revenue
we draw three plot to explore the relationship between revenue, army base loation and time.

### 1. Distribution of Numerical Columns
We analyzed two numerical variables — Revenue and NAFI Amt — to understand their distribution patterns. To improve visualization, we:
- Removed outliers using the Interquartile Range (IQR) method.
- Plotted histograms with kernel density estimates (KDE) to observe distribution and skewness.

Both variables showed similar patterns. Upon further research, we found that NAFI stands for Nonappropriated Fund Instrumentality, representing funds derived from slot machine revenue (essentially a fixed proportion of the revenue). Therefore, in subsequent analyses, we focus solely on Revenue, as it sufficiently captures the underlying trends.

### 2. Revenue by Location
Revenue was aggregated by Location to calculate the average revenue per site. The results were sorted by mean revenue to highlight the Top 10 locations with the highest average slot machine revenue. The plot shows that the top three Marine bases have significantly higher mean slot machine revenue compared to other Army bases, suggesting a potential concentration of gambling activity at these locations.

### 3. Monthly Revenue Trend
This analysis helps us understand the time-based dynamics of gambling engagement across all military bases. We examined two subgroups:
- The mean monthly revenue across all locations.
- The mean monthly revenue across the Top 10 highest-revenue locations.

Two plots were generated:
- The first shows how average revenue changes over time
- The second aggregates revenue by month (across different years) to identify which months generally have higher average revenue.

The results indicate that the Top 10 bases do not differ significantly from other bases in their overall and seasonal trends. Both gambling activity among soldiers dropped sharply in 2020, likely due to the COVID-19 pandemic. There is a clear seasonal pattern — soldiers tend to gamble more in March and May, a trend that warrants further investigation.

---


## Visualization Findings- Navy revenue
Presenting the distribution and yearly trends of slot machine revenue across countries and individual installations.

# Data - Navy revenue report 1

### 1. Year-wise Total Revenue (FY16–FY22)

The bar charts display total Slot Machine Revenue and NAFI Reimbursements by fiscal year. Both categories show a generally increasing trend over time, with FY22 recording the highest overall revenue. Although slight fluctuations occur during intermediate years, the overall pattern suggests consistent financial growth and operational expansion across the Navy’s global network.

### 2. Country-wise Total Revenue (FY16–FY22)

The comparative horizontal bar chart highlights striking regional disparities. Japan dominates both Slot and NAFI revenues, far surpassing all other countries combined. Italy and Spain rank next but at much lower levels, while Korea, Malaysia, and Greece contribute marginally. This distribution emphasizes Japan’s crucial role in sustaining the overall revenue structure of the Navy’s overseas programs.

### 3. Time-Trend Analysis (FY16–FY22)

The line charts trace revenue trends by country across fiscal years. Japan consistently maintains the highest revenue levels and exhibits steady growth after a temporary decline around FY20. Italy and Spain demonstrate moderate and stable contributions, while other countries remain comparatively low. These trends collectively illustrate Japan’s sustained dominance and the gradual strengthening of key regional installations over the observed period.

# Data - Navy revenue report 2
We divided the Navy revenue data into two CSV files. The first file, Navy Revenue Table, presents the revenue by country and installation from FY18 to FY24. The second file, Monthly Revenue Report, provides a detailed breakdown of monthly revenues for each installation.

### 1.Average Slot Revenue per Installation by Country (FY18–FY24)
The bar chart illustrates the average slot machine revenue per installation across different countries. Among all, Japan stands out significantly, generating the highest average revenue per installation.
This exceptional figure may suggest that U.S. military bases in Japan experience higher engagement or potential gambling-related concerns compared to other overseas locations.

### 2.Slot Machine Revenue by Installation (FY18–FY24)
The line chart further breaks down slot machine revenue trends by individual installations.
The analysis clearly identifies Yokosuka and Sasebo, both located in Japan, as the top two installations with the highest slot revenues.
This finding aligns with the previous chart, reinforcing the observation that Japanese-based installations are key contributors to overall slot revenue among U.S. overseas bases.

---

# Data - Financial Statements
The Financial Statements data can be broken up into four sections
 - Overall Asset/Liability Balance for a given month
 - Actual vs Budgeted Operating Results for a given month 
 - Operating Revenues by Branch of Service over several previous months
 - Revenue by Base for a given month (as well as YTD revenue)

Unfortunately, due to difficulties in finding proper tools to parse this data, I only have access to a partial  Overall Asset/Liability Balance for this data analysis. This will limit the ability to perform more complex analysis of the full dataset, but there are still insights that can be gleaned

### 1. Total Operational Cash On Hand Compared To Total Equity
This line chart compares the monthly Operational Cash compared to the total Equity of the Army Recreation Machine Program. Prior to 2022, Cash was recorded under a single line item, but after this it is split into Restricted Cash and Operational Cash. This analysis shows that while cash steadily grew from 2020 until the beginning of 2023, it has downturned sharply due to the complete depletion of Restricted Cash, which began to decline starting in 2022 and sharpened in 2023. As well, it is notable that the total equity has remained at the exact same value (down to the cent) since 10/31/2021. This is not a parsing error, as review of the original dataset confirms all entries past this point have the *exact* same value.

### 2. Total Asset Value Compared To Assets - Deprecation (Combined Asset Value)
This line chart displays the trend of  Asset Values in comparison to the Combined Asset value, which takes into account asset deprecation. Combined asset values steadily declined from ~$16 million in 2020 to under $7 million at the end of 2022, before shooting up to $20 million by April of 2024, due in part to both a decrease in deprecation alongside an increase in asset value.




# Data - FY2024 Asset Report (EGMs by Region, Service)

## Data Extraction & Cleaning Steps - FY2024 Asset Report

### 1. Data Extraction
The “EGMs by Region, Service” table was extracted directly from the **FY2024 Asset Report (PDF)** using a Python-based PDF parsing pipeline.  
This process involved:
- Identifying and isolating the **EGMs by Region, Service** section from each monthly page.
- Capturing tabular structures using `pdfplumber` and converting them into a structured CSV format.
- Automatically extracting and standardizing the `Period`, `Region`, `Army`, `Navy`, `Marine_Corps`, `Airforce`, and `Total` columns.

### 2. Data Cleaning
After extraction, the dataset underwent cleaning to ensure analytical consistency:
- Removed all rows labeled **“Total”** under the `Region` column to avoid double-counting.
- Normalized numeric values by removing commas and converting them to float.
- Standardized month and year information into integer columns (`Month`, `Year`).
- Sorted the final dataset chronologically by `Year`, `Month`, and `Region`.

---

## Visualization Findings - FY2024 Asset Report

### 1. Share of EGMs by Region
A pie chart was generated to visualize the share of EGMs across **Europe**, **Japan**, and **Korea** in FY2024.  
The analysis shows:
- **Europe** holds the largest share of EGMs (**39.4%**).  
- **Japan** follows closely with **37.8%**.  
- **Korea** accounts for **22.8%** of total EGMs.  

This distribution indicates that Europe remains the most significant operational area for EGMs, while Japan continues to play a comparably strong role in overall slot machine operations.

### 2. Overall EGM Composition by Service
A second pie chart summarizes the overall EGM composition by military branch.  
The results show:
- **Army** dominates with **55.7%** of total EGMs.  
- **Navy** accounts for **25.4%**.  
- **Marine Corps** contributes **19.0%**.  
- **Airforce** has no recorded EGMs (0%).  

This finding highlights that the **Army operates more than half of all EGMs**, making it the primary service managing gambling operations across regions.

### 3. EGM Distribution by Service and Region
A grouped bar chart compares EGM counts by service branch across Europe, Japan, and Korea.  
The analysis reveals that:
- **Europe** leads in Army-operated EGMs.  
- **Japan** shows the strongest presence of Marine Corps EGMs.  
- **Korea** maintains moderate Army dominance but fewer Navy installations.  

These variations suggest region-specific differences in the allocation and management of EGMs among the military branches.

### 4. Monthly EGM Trend by Region
A line chart displays monthly changes in EGM totals throughout FY2024.  
Key observations include:
- **Europe’s** EGM totals remain consistently higher than other regions across all months.  
- **Japan’s** EGM count stays relatively stable with minimal fluctuation.  
- **Korea’s** EGM levels show a slight decline during mid-year but recover toward year-end.  

This pattern suggests stable EGM operations overall, with **Europe serving as the steady core region** of slot machine activity.

Through the analysis of the **EGMs by Region, Service** dataset from the **FY2024 Asset Report**,  
it is evident that the **Army and Europe** dominate the global distribution of EGMs.  
The findings imply a centralized concentration of gambling operations within European installations  
and a consistently strong presence in Japan.  
These insights help illuminate operational priorities and regional engagement trends across military branches.

## FY2021 Asset Report — Exploratory Data Analysis (EDA)

### Overview:
The EDA for the FY2021 Asset Report focuses on understanding asset distribution, identifying structural inconsistencies caused by COVID-era reporting, and validating the integrity of the extracted tables. Due to unique formatting in the FY2021 report, the dataset required additional cleaning and normalization before analysis.

### Key Analyses Conducted:

- **Asset Distribution by Region & Service**: Examined geographic patterns and service-level variations to validate that regional summary data aligned with extracted field-office tables.
- **Asset Characteristics & Metadata**: Profiled asset types, manufacturers, installation locations, and usage classifications to identify anomalies introduced by irregular table formatting.
- **COVID-Specific Fields**: Assessed the presence and impact of temporary COVID-related categories to ensure they did not distort cross-year comparisons.
- **Years in Storage Patterns**: Analyzed storage duration and asset aging trends using the pivot output derived from the extraction process.
- **Field Office vs. Operational Status Consistency**: Compared extracted “Site Operational Status” tables with field-office asset counts to verify internal consistency across tables.

### Data Validation & Cleaning Steps:
- Addressed inconsistent headers and merged cell artifacts remaining after extraction.
- Standardized column names and data types to match schemas used across other fiscal years.
- Checked for duplicated rows and missing values resulting from PDF formatting issues.
- Ensured alignment between summary tables and detailed asset-level tables.

### Notebook Usage:
The full analysis is documented in `FY2021_Asset_Report_EDA.ipynb`.
To replicate the EDA:
1. Ensure the cleaned CSV outputs from the FY2021 extraction workflow are available.
2. Open the notebook and run cells sequentially.
3. Visualizations and summary tables included in the notebook provide insight into data quality, distribution patterns, and irregularities unique to FY2021.

