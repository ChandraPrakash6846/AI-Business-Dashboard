# 📊 AI Business Dashboard

An AI-powered Business Dashboard that analyzes business datasets, creates interactive visualizations, provides insights, and allows users to ask questions in natural language.

> **No API Key Required** — All AI features use built-in statistical analysis.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 📁 **Data Upload** | Upload CSV, Excel (.xlsx/.xls), and SQLite databases |
| 🧹 **Auto Cleaning** | Removes duplicates, fills missing values, detects outliers, converts date columns |
| 📈 **KPI Cards** | Auto-detects Sales, Revenue, Profit, Customers with growth metrics |
| 📊 **Interactive Charts** | Bar, Line, Pie, Scatter, Histogram, Box Plot, Area — all interactive (Plotly) |
| 🔍 **Advanced Analysis** | Trend analysis with moving averages, Pearson correlation matrix, Z-score anomaly detection |
| 🤖 **AI Insights** | Statistical engine generates 8-10 business insights with recommendations |
| 💬 **Natural Language Queries** | Ask questions like "What is the total revenue by region?" |
| 📥 **Export Reports** | Download Excel workbooks and PDF reports |
| 📜 **Analysis History** | SQLite-backed log of all analysis actions |

---

## 🚀 Quick Start (3 Steps)

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Dashboard

```bash
streamlit run app.py
```

### 3. Open in Browser

The app opens automatically at **http://localhost:8501**

---

## 📂 Project Structure

```
ai-business-dashboard/
├── app.py                      # Main Streamlit application
├── requirements.txt            # Python dependencies
├── README.md                   # Project documentation
├── test_dashboard.py           # Integration test suite
├── utils/
│   ├── __init__.py
│   ├── data_loader.py          # CSV/Excel/SQLite upload handler
│   ├── data_cleaner.py         # Auto data cleaning & validation
│   ├── kpi_generator.py        # KPI detection & calculation
│   ├── chart_generator.py      # Plotly chart factory functions
│   ├── analysis.py             # Trend, correlation & anomaly analysis
│   ├── ai_insights.py          # Rule-based AI insight engine
│   ├── nl_query.py             # Natural language query processor
│   ├── export_utils.py         # Excel & PDF export
│   └── history.py              # SQLite analysis history tracker
├── sample_data/
│   └── sample_sales.csv        # Built-in sample dataset
└── assets/
    └── style.css               # Custom dashboard styling
```

---

## 🛠 Technology Stack

| Technology | Purpose |
|-----------|---------|
| **Python 3.10+** | Core programming language |
| **Streamlit** | Web dashboard framework |
| **Pandas** | Data manipulation and analysis |
| **Plotly** | Interactive chart visualizations |
| **NumPy** | Numerical computations |
| **SciPy** | Statistical analysis (Z-scores, Shapiro-Wilk, correlation) |
| **SQLAlchemy** | Database connectivity |
| **SQLite** | Analysis history storage |
| **openpyxl** | Excel file reading/writing |
| **fpdf2** | PDF report generation |

---

## 📖 User Manual

### Uploading Data

1. Click **"Browse files"** in the sidebar or drag & drop your file
2. Supported formats: `.csv`, `.xlsx`, `.xls`, `.db`, `.sqlite`
3. Or check **"Use Sample Data"** to explore with the built-in dataset

### Data Cleaning (Automatic)

When data is loaded, the system automatically:
- Removes exact duplicate rows
- Fills missing numeric values with column median
- Fills missing categorical values with most frequent value
- Converts date-like strings to datetime format
- Detects outliers using the IQR method

A cleaning summary appears in the sidebar.

### Dashboard Page

- **KPI Cards**: Auto-detected metrics (Sales, Revenue, Profit, Customers, Cost, Rating) with growth percentages
- **Interactive Charts**: Select chart type, X/Y axes, and optional color grouping
- **Data Preview**: Expandable raw data view and summary statistics

### Analysis Page

- **Trend Analysis**: Select date and value columns to see moving averages and growth rate
- **Correlation**: Pearson correlation heatmap with strong correlation pairs highlighted
- **Anomaly Detection**: Z-score based detection with adjustable threshold
- **Distribution**: Statistical tests, histogram, and box plot for any numeric column

### AI Insights Page

Automatically generates 8-10 insights covering:
- Top performers by category
- Growth trends over time
- Concentration risk analysis
- Outlier detection
- Correlation patterns
- Seasonal patterns
- Distribution skewness
- Data quality assessment

Each insight includes a priority level and actionable recommendation.

### Ask Questions Page

Type natural language questions about your data:
- `"What is the total revenue?"` → Calculates the sum
- `"Show profit by region"` → Groups data and creates a chart
- `"Top 5 products by revenue"` → Shows the top performers
- `"Show sales trend"` → Displays a time series chart
- `"Distribution of profit"` → Shows a histogram

### Export Page

- **Excel Report**: Multi-sheet workbook (Data, Summary, KPIs, Insights)
- **PDF Report**: Formatted report with KPIs, insights, and statistical summary
- **Clean Data**: Download the cleaned dataset as CSV or Excel

### History Page

View a timeline of all analysis actions performed during the session. Includes timestamps, action types, and result summaries.

---

## 🧪 Testing

Run the integration test suite:

```bash
python test_dashboard.py
```

This verifies all 24 features: data loading, cleaning, KPI generation, all chart types, correlation, anomaly detection, trend analysis, distribution analysis, AI insights, NL queries, export, and history.

---

## 📋 Requirements

See `requirements.txt` for full list:

```
streamlit>=1.28.0
pandas>=2.0.0
plotly>=5.18.0
openpyxl>=3.1.0
xlsxwriter>=3.1.0
fpdf2>=2.7.0
scipy>=1.11.0
numpy>=1.24.0
sqlalchemy>=2.0.0
```

---

## 🔮 Future Enhancements

- **Ollama/LLM Integration**: Optional local LLM for more advanced natural language processing
- **Real-time Data**: Connect to live databases and APIs
- **Custom Dashboards**: Drag-and-drop dashboard builder
- **Collaboration**: Multi-user support with shared analysis
- **Automated Reports**: Scheduled report generation and email delivery

---

## 📄 License

This project is created for educational purposes as part of an internship assignment.
