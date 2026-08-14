# AI Business Dashboard - User Manual 📘

Welcome to the **AI Business Dashboard** User Manual. This guide provides step-by-step instructions for non-technical business users, analysts, and managers to maximize the value of this AI-powered data platform.

---

## 🎯 Quick Start Guide

### Step 1: Ingesting Data
- Open the application in your web browser.
- On the left sidebar under **📁 Select Data Source**, choose one of 3 options:
  1. **Upload File (CSV/Excel)**: Click "Browse files" to upload your business spreadsheet (`.csv`, `.xlsx`, `.xls`).
  2. **Use Built-in Sample Dataset**: Instantly loads our pre-packaged retail dataset with 26 transactions.
  3. **Connect SQL Database**: Connect to a local SQLite database or remote MySQL/PostgreSQL server.

---

### Step 2: Exploring Executive KPIs & Data Health
- Upon loading a dataset, the **Header Banner** displays automated cleaning statistics (e.g., duplicates removed, missing values imputed).
- **KPI Metric Cards** at the top provide instant visibility into:
  - Total Sales & Order Count
  - Net Profit & Profit Margin %
  - Average Order Value (AOV)
  - Customer / Unique Entity Count

---

### Step 3: Generating Custom Visualizations
1. Click on the **📈 Interactive Visualizations** tab.
2. Select your desired chart type from the dropdown:
   - **Bar Chart**: Ideal for categorical comparisons (e.g., Sales by Region).
   - **Line Chart**: Best for time-series trend analysis (e.g., Monthly Sales).
   - **Pie / Donut Chart**: Shows percentage market share per segment.
   - **Scatter Plot**: Explores relationships between two numerical factors (e.g., Sales vs Profit).
   - **Box Plot**: Displays value distribution and highlights outliers.
3. Select your X-Axis, Y-Axis, and optional Grouping column.

---

### Step 4: Machine Learning & Anomaly Diagnostics
1. Click on the **🔍 Advanced Analytics & Anomalies** tab.
2. View the **Pearson Correlation Matrix Heatmap** to spot strong positive/negative metric relationships.
3. Switch to **🚨 Anomaly Detection (ML)** and click **Run Isolation Forest Anomaly Scan** to flag suspicious transactions or operational outliers.
4. Read **💡 AI Executive Insights** for automated strategic recommendations.

---

### Step 5: Natural Language Data Querying
1. Click on the **🤖 Natural Language Queries** tab.
2. Type any question in plain English or click a preset shortcut button:
   - *"Total sales by category"*
   - *"Which region generated highest profit?"*
   - *"Show sales over time"*
3. Click **🚀 Ask Assistant** to view generated text answers, filtered tables, and dynamic charts.

---

### Step 6: Exporting Reports
- Click **📥 Download PDF Report** at the top of the dashboard for a print-ready executive summary.
- Click **📥 Export Excel Report** to download a formatted multi-tab spreadsheet containing raw data, KPIs, and AI insights.

---

## 💡 Frequently Asked Questions (FAQ)

**Q: Do I need an OpenAI API key to use this app?**  
A: No! The application includes a built-in statistical fallback AI engine that generates insights 100% offline. Adding an API key is optional.

**Q: Where is analysis history saved?**  
A: History is stored locally in `dashboard_history.db` (SQLite) on your machine. You can view or clear history anytime in the **📜 Analysis History** tab.
