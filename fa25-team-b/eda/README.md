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

# Data - Navy revenue
We divided the Navy revenue data into two CSV files. The first file, Navy Revenue Table, presents the revenue by country and installation from FY18 to FY24. The second file, Monthly Revenue Report, provides a detailed breakdown of monthly revenues for each installation.

## Visualization Findings- Navy revenue
Presenting the distribution and yearly trends of slot machine revenue across countries and individual installations.

### 1.Average Slot Revenue per Installation by Country (FY18–FY24)
The bar chart illustrates the average slot machine revenue per installation across different countries. Among all, Japan stands out significantly, generating the highest average revenue per installation.
This exceptional figure may suggest that U.S. military bases in Japan experience higher engagement or potential gambling-related concerns compared to other overseas locations.

### 2.Slot Machine Revenue by Installation (FY18–FY24)
The line chart further breaks down slot machine revenue trends by individual installations.
The analysis clearly identifies Yokosuka and Sasebo, both located in Japan, as the top two installations with the highest slot revenues.
This finding aligns with the previous chart, reinforcing the observation that Japanese-based installations are key contributors to overall slot revenue among U.S. overseas bases.



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


