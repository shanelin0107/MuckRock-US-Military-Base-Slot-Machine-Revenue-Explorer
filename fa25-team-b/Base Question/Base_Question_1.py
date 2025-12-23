import os

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.ticker as mtick

OUTPUT_DIR = "plots"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def save_plot(fig, filename):
    """Save matplotlib figure to the plots directory as a PNG."""
    path = os.path.join(OUTPUT_DIR, filename)
    fig.savefig(path, dpi=300, bbox_inches='tight')
    print(f"Saved plot: {path}")

# =========================================================
# 1. Load Data
# =========================================================
file_path = "District_Revenue_FY20-FY24_with_lat_lon_clean.csv"

# file_path = "data/District_Revenue_FY20-FY24_with_lat_lon_clean.csv"

df = pd.read_csv(file_path)

# =========================================================
# 2. Filter Data to Revenue Only
# =========================================================
df_revenue = df[df['Category'] == 'Revenue'].copy()

# =========================================================
# 3. Data Cleaning
# =========================================================
if df_revenue.columns[0].startswith('\ufeff'):
    df_revenue = df_revenue.rename(columns={df_revenue.columns[0]: 'Service'})


df_revenue['Amount'] = pd.to_numeric(df_revenue['Amount'], errors='coerce')


cols_to_check = ['Service', 'Region', 'Base', 'Amount']
df_revenue = df_revenue.dropna(subset=cols_to_check)

# =========================================================
# 4. Aggregation & Analysis
# =========================================================

# ---- (A) Summary by Service and Region ----
service_region_summary = (
    df_revenue
    .groupby(['Service', 'Region'])
    .agg(
        total_revenue=('Amount', 'sum'),
        n_bases=('Base', 'nunique')
    )
    .reset_index()
)

service_region_summary['per_base_revenue'] = (
    service_region_summary['total_revenue'] / service_region_summary['n_bases']
)


service_region_summary = (
    service_region_summary
    .sort_values(by='total_revenue', ascending=False)
    .reset_index(drop=True)
)

# ---- (B) Summary by Individual Base ----
base_summary = (
    df_revenue
    .groupby(['Base', 'Service', 'Region'])
    .agg(
        total_revenue=('Amount', 'sum')
    )
    .reset_index()
)

base_summary = (
    base_summary
    .sort_values(by='total_revenue', ascending=False)
    .reset_index(drop=True)
)

# ---- (C) Table chart: Total & Per-base Revenue by Branch x Region ----
table_chart = service_region_summary[[
    'Service', 'Region', 'n_bases', 'total_revenue', 'per_base_revenue'
]].copy()

table_chart_formatted = table_chart.copy()
table_chart_formatted['total_revenue'] = table_chart_formatted['total_revenue'].map('${:,.0f}'.format)
table_chart_formatted['per_base_revenue'] = table_chart_formatted['per_base_revenue'].map('${:,.0f}'.format)

# =========================================================
# 5. Save Summary Tables to CSV
# =========================================================
service_region_summary.to_csv("service_region_summary_by_service_region.csv", index=False)
base_summary.to_csv("base_summary_total_revenue.csv", index=False)
table_chart.to_csv("table_chart_service_region.csv", index=False)

# 另存 Markdown 表格
md_lines = [
    "| Military Branch | Region | # Bases | Total Slot Revenue | Per-Base Slot Revenue |",
    "| --- | --- | --- | --- | --- |",
]
for row in table_chart.itertuples(index=False):
    md_lines.append(
        f"| {row.Service} | {row.Region} | {row.n_bases} | "
        f"${row.total_revenue:,.0f} | ${row.per_base_revenue:,.0f} |"
    )

with open("table_chart_service_region.md", "w") as f:
    f.write("\n".join(md_lines))

pd.options.display.float_format = '${:,.2f}'.format

print("--- TABLE: TOTAL AND PER-BASE REVENUE BY SERVICE AND REGION ---")
print(table_chart_formatted.to_string(index=False))
print("\n" + "="*80 + "\n")

print("--- SUMMARY: REVENUE BY SERVICE AND REGION (TOP 20) ---")
print(service_region_summary.head(20))
print("\n" + "="*80 + "\n")

print("--- SUMMARY: REVENUE BY INDIVIDUAL BASE (TOP 20) ---")
print(base_summary.head(20))
print("\n" + "="*80 + "\n")

# =========================================================
# 6. Visualizations (All Saved to Files)
# =========================================================
sns.set_theme(style="whitegrid")

# ---------- Plot 1: Total Revenue by Region and Service ----------
fig, ax = plt.subplots(figsize=(12, 6))
bar_plot = sns.barplot(
    data=service_region_summary,
    x='Region',
    y='total_revenue',
    hue='Service',
    ax=ax
)

bar_plot.yaxis.set_major_formatter(
    mtick.FuncFormatter(lambda x, p: f'${x/1e6:.1f}M')
)

ax.set_title('Total Slot Machine Revenue by Region and Military Branch', fontsize=16)
ax.set_xlabel('Region', fontsize=12)
ax.set_ylabel('Total Revenue (Millions USD)', fontsize=12)
plt.setp(ax.get_xticklabels(), rotation=30, ha='right')
ax.legend(title='Service')
fig.tight_layout()

save_plot(fig, "total_revenue_by_region_and_service.png")
plt.close(fig)

# ---------- Plot 2: Per-Base Revenue Heatmap ----------
#  Service x Region 的 pivot table
heatmap_data = service_region_summary.pivot(
    index='Service',
    columns='Region',
    values='per_base_revenue'
)

fig, ax = plt.subplots(figsize=(10, 6))
hm = sns.heatmap(
    heatmap_data,
    annot=True,
    fmt=",.0f",  
    cbar_kws={'format': mtick.FuncFormatter(lambda x, p: f'${x:,.0f}')},
    ax=ax
)

ax.set_title('Average Revenue Per Base by Service and Region', fontsize=16)
ax.set_xlabel('Region', fontsize=12)
ax.set_ylabel('Service', fontsize=12)
fig.tight_layout()

save_plot(fig, "per_base_revenue_heatmap_service_region.png")
plt.close(fig)

# ---------- Plot 3 (Optional): Top 10 Bases by Total Revenue ----------
top_n = 10
top_bases = base_summary.head(top_n).copy()

fig, ax = plt.subplots(figsize=(12, 6))
base_plot = sns.barplot(
    data=top_bases,
    x='Base',
    y='total_revenue',
    hue='Service',
    ax=ax
)

base_plot.yaxis.set_major_formatter(
    mtick.FuncFormatter(lambda x, p: f'${x/1e6:.1f}M')
)

ax.set_title(f'Top {top_n} Bases by Slot Machine Revenue', fontsize=16)
ax.set_xlabel('Base', fontsize=12)
ax.set_ylabel('Total Revenue (Millions USD)', fontsize=12)
plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
ax.legend(title='Service')
fig.tight_layout()

save_plot(fig, "top10_bases_total_revenue.png")
plt.close(fig)

# =========================================================
# 7. Text Summary / Interpretation
# =========================================================
top_total = service_region_summary.iloc[0]

top_per_base = service_region_summary.sort_values(
    by='per_base_revenue',
    ascending=False
).iloc[0]

summary_text_1 = (
    f"1. HIGHEST TOTAL REVENUE: "
    f"The {top_total['Service']} in {top_total['Region']} generated the highest total revenue, "
    f"with ${top_total['total_revenue']:,.2f} across {int(top_total['n_bases'])} base(s)."
)

summary_text_2 = (
    f"2. HIGHEST REVENUE PER BASE: "
    f"The {top_per_base['Service']} in {top_per_base['Region']} had the highest average revenue per base, "
    f"at ${top_per_base['per_base_revenue']:,.2f} per base."
)

print("--- ANALYSIS SUMMARY ---")
print(summary_text_1)
print(summary_text_2)

with open("analysis_summary_service_region.txt", "w") as f:
    f.write("--- ANALYSIS SUMMARY ---\n")
    f.write(summary_text_1 + "\n")
    f.write(summary_text_2 + "\n")
