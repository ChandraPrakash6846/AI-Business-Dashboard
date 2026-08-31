# AI Business Dashboard - Fully Updated & Verified

> **Internship Assignment Project Submission**  
> **Developer / Author:** Chandra Prakash Choudhary  
> **GitHub:** [ChandraPrakash6846](https://github.com/ChandraPrakash6846)  
> **LinkedIn:** [Chandra Prakash Choudhary](https://www.linkedin.com/in/chandra-prakash-choudhary-17b96b212/)  
> **Domain:** Artificial Intelligence & Business Intelligence  
> **Objective:** Design and implement an AI-powered Business Dashboard that automates data cleaning, generates executive KPI cards, renders interactive visualizations, conducts statistical anomaly diagnostics, answers natural language data queries, and exports PDF/Excel reports.


---

## 📋 Internship Assignment Compliance Checklist

This project was built to satisfy all requirements specified in the Internship Assignment specification:

| # | Requirement | Status | Project Implementation |
| :--- | :--- | :---: | :--- |
| 1 | **Upload CSV/Excel & Multi-File Datasets** | ✅ **Passed** | Built-in file uploader supporting single & multi-file concatenation/merging. |
| 2 | **Connect to a SQL database** *(Optional Bonus)* | ✅ **Passed** | `SQLAlchemy` integration supporting SQLite, PostgreSQL, and MySQL. |
| 3 | **Automatically clean and validate data** | ✅ **Passed** | Auto-detects dates, imputes missing values (median/mode), and trims duplicates. |
| 4 | **Generate KPI cards** | ✅ **Passed** | Dynamic metric cards: Sales, Net Profit, Profit Margin %, AOV, Orders, Customers. |
| 5 | **Create interactive charts and dashboards** | ✅ **Passed** | Plotly interactive visualizer (Bar, Line, Pie, Scatter, Box plot) with theme toggles. |
| 6 | **Perform trend, correlation, and anomaly analysis** | ✅ **Passed** | Pearson correlation heatmap + `Scikit-Learn` `IsolationForest` anomaly scan. |
| 7 | **Provide AI-generated business insights** | ✅ **Passed** | Statistical executive insight engine + optional OpenAI/Ollama LLM integration. |
| 8 | **Support natural language queries** | ✅ **Passed** | Plain English query interpreter with text filtering and auto-chart rendering. |
| 9 | **Export reports in PDF or Excel format** | ✅ **Passed** | 1-click PDF Report generator (`ReportLab`) & formatted Excel exporter (`openpyxl`). |
| 10 | **Maintain analysis history** | ✅ **Passed** | SQLite database (`dashboard_history.db`) tracking dataset sessions and query logs. |


---

## 🌟 Key Technical Features

1. **Universal Multi-File Auto-Merger & Relational Database Auto-Joiner (`modules/data_processor.py`)**
   - Supports uploading single or multiple files (`.csv`, `.xlsx`, `.sql`, `.db`) simultaneously.
   - Automatically detects relational database schemas (Sakila, Northwind, ClassicModels) and performs foreign-key joins (`orders` + `orderdetails` + `customers` + `employees` + `offices`).

2. **SQL Script (.sql) Dialect Engine (`modules/sql_connector.py`)**
   - Parses raw `.sql` script dumps (MySQL / PostgreSQL / SQLite), strips incompatible DDL constraints, and executes statements into a unified SQLite database engine.

3. **Machine Learning Anomaly Engine (`modules/ai_engine.py`)**
   - Implements Scikit-learn's `IsolationForest` unsupervised learning model to scan numerical fields for statistical business anomalies and high-risk transactions.

4. **Natural Language Processing Assistant (`components/nl_query.py`)**
   - Translates user questions like *"Total sales by category"* or *"Profit by region"* into filtered Pandas DataFrames and renders tailored Plotly charts instantly.

5. **Executive PDF & Excel Reporting Engine (`modules/export_engine.py`)**
   - Generates publication-ready PDF summaries with ReportLab and multi-tab structured Excel workbooks with openpyxl.


---

## 🏗️ Project Architecture

```
ai-business-dashboard/
├── app.py                      # Main Streamlit application & layout
├── config.py                   # Glassmorphism theme & CSS design system
├── components/
│   ├── sidebar.py              # File uploader, SQL database connector & settings
│   ├── kpi_cards.py            # Dynamic KPI metric cards component
│   ├── charts.py               # Plotly interactive chart visualizer
│   ├── analytics.py            # Correlation matrix & Isolation Forest anomaly scan
│   ├── nl_query.py             # Natural Language Query Engine UI
│   └── history.py              # SQLite session & query history log
├── modules/
│   ├── data_processor.py       # Data cleaner, validator & column mapper
│   ├── sql_connector.py        # SQLAlchemy database connection manager
│   ├── ai_engine.py            # Statistical engine & NL query interpreter
│   ├── export_engine.py        # PDF & Excel report generator
│   └── database.py             # SQLite database history manager
├── sample_data/
│   └── retail_sales_sample.csv # Sample dataset for instant evaluation
├── requirements.txt            # Python dependencies list
├── README.md                   # Technical assignment submission docs
├── USER_MANUAL.md              # User manual & visual feature guide
├── PRESENTATION.html           # Interactive HTML slide deck for project defense
├── DEMO_GUIDE.md               # Video demo script & walkthrough guide
└── test_dashboard.py           # Automated test suite
```

---

## ⚙️ Quick Start & Installation

1. **Clone/Navigate to Project Directory**:
   ```bash
   cd ai-business-dashboard
   ```

2. **Install Python Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Launch the Dashboard**:
   ```bash
   streamlit run app.py
   ```

4. Open your web browser at `http://localhost:8501`.

---

## 📂 Expected Deliverables Summary

- **Source Code**: Clean, modular Python code structured into `modules/` and `components/`.
- **Project Documentation**: [README.md](file:///C:/Users/choud/.gemini/antigravity/scratch/ai-business-dashboard/README.md)
- **User Manual**: [USER_MANUAL.md](file:///C:/Users/choud/.gemini/antigravity/scratch/ai-business-dashboard/USER_MANUAL.md)
- **Presentation**: [PRESENTATION.html](file:///C:/Users/choud/.gemini/antigravity/scratch/ai-business-dashboard/PRESENTATION.html)
- **Demo Script**: [DEMO_GUIDE.md](file:///C:/Users/choud/.gemini/antigravity/scratch/ai-business-dashboard/DEMO_GUIDE.md)

---

## 📄 License & Evaluation
Created as an Internship Assignment Submission under the MIT License.
