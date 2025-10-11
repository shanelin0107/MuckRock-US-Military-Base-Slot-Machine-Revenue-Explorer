# Data Cleaning Steps

## 1. Columns Containing Numeric (Fiscal) Values
For columns that contain fiscal or monetary numbers, the following cleaning steps are applied:

- Convert each value to a string and strip leading/trailing whitespace.  
- Use regular expressions to remove non-numeric symbols** such as `$`, commas, and other special characters.  
- Convert the cleaned string to a floating-point number (`float`).  
- Detect and handle parentheses indicating negative values — e.g., `(1,200)` → `-1200.0`.  
- Replace missing or unparsable values with `0.0`.


## 2. Columns Containing Month or Date Information
For columns representing months or dates, the following cleaning logic is used:

- Normalize valid month strings into a standardized `YYYY-MM` format.  
- Let pandas automatically infer the date format and return the value in `YYYY-MM-DD` format.  
- If all parsing attempts fail, return an empty string.

---


# Visualization Findings
we draw three plot to explore the relationship between revenue, army base loation and time.

## 1. Distribution of Numerical Columns
We analyzed two numerical variables — Revenue and NAFI Amt — to understand their distribution patterns. To improve visualization, we:
- Removed outliers using the Interquartile Range (IQR) method.
- Plotted histograms with kernel density estimates (KDE) to observe distribution and skewness.

Both variables showed similar patterns. Upon further research, we found that NAFI stands for Nonappropriated Fund Instrumentality, representing funds derived from slot machine revenue (essentially a fixed proportion of the revenue). Therefore, in subsequent analyses, we focus solely on Revenue, as it sufficiently captures the underlying trends.

## 2. Revenue by Location
Revenue was aggregated by Location to calculate the average revenue per site. The results were sorted by mean revenue to highlight the Top 10 locations with the highest average slot machine revenue. The plot shows that the top three Marine bases have significantly higher mean slot machine revenue compared to other Army bases, suggesting a potential concentration of gambling activity at these locations.

## 3. Monthly Revenue Trend
