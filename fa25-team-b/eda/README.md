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

---

# Data - Financial Statements
The Financial Statements data can be broken up into four sections
 - Overall Asset/Liability Balance for a given month
 - Actual vs Budgeted Operating Results for a given month 
 - Operating Revenues by Branch of Service over several previous months
 - Revenue by Base for a given month (as well as YTD revenue)

Unfortunately, due to difficulties in finding proper tools to parse this data, I only have access to a partial  Overall Asset/Liability Balance for this data analysis. This will limit the ability to perform more complex analysis of the full dataset, but there are still insights that can be gleaned

### 1. Total Operational Cash On Hand Compared To Total Equity
This line chart compares the monthly Operational Cash compared to the total Equity of the Amry Recreation Machine Program. Prior to 2022, Cash was recorded under a single line item, but after this it is split into Restricted Cash and Operational Cash. This analysis shows that while cash steadily grew from 2020 until the beginning of 2023, it has downturned sharply in due to the complete depletion of Restricted Cash, which began to decline starting in 2022 and sharpened in 2023. As well, it is notable that the total equity has remained at the exact same value (down to the cent) since 10/31/2021. This is not a parsing error, as review of the original dataset confirms all entries past this point have the *exact* same value.

### 2. Total Asset Value Compared To Assets - Deprecation (Combined Asset Value)
This line chart displays the trend of  Asset Values in comparison to the Combined Asset value, which takes into account asset deprecation. Combined asset values steadily declined from ~$16 million in 2020 to under $7 million at the end of 2022, before shooting up to $20 million by April of 2024, due in part to both a decrease in deprecation alongside an increase in asset value.



