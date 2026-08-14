import streamlit as st
import os
import pandas as pd
from modules.data_processor import load_dataset
from modules.sql_connector import create_db_engine, list_tables, load_table_data

SAMPLE_CSV = os.path.join(os.path.dirname(__file__), "..", "sample_data", "retail_sales_sample.csv")

def render_sidebar():
    """
    Renders sidebar for dataset input, SQL configuration, and settings.
    Returns: (df, dataset_name, llm_config)
    """
    st.sidebar.image("https://img.icons8.com/isometric/100/combo-chart.png", width=60)
    st.sidebar.title("AI Business Dashboard")
    st.sidebar.caption("🎓 Internship Capstone Project • AI & Data Science")
    st.sidebar.markdown("""
    <div style="background: rgba(37, 99, 235, 0.15); border: 1px solid #2563EB; padding: 10px 12px; border-radius: 8px; margin-bottom: 15px;">
        <small style="color: #60A5FA; font-weight: 700;">👨‍💻 Chandra Prakash Choudhary</small><br/>
        <small style="color: #94A3B8;">AI & Business Analytics Intern</small><br/>
        <small><a href="https://github.com/ChandraPrakash6846" target="_blank" style="color: #38BDF8;">GitHub</a> • <a href="https://www.linkedin.com/in/chandra-prakash-choudhary-17b96b212/" target="_blank" style="color: #38BDF8;">LinkedIn</a></small>
    </div>
    """, unsafe_allow_html=True)

    st.sidebar.divider()


    data_source = st.sidebar.radio(
        "📁 Select Data Source",
        ["Upload File (CSV/Excel)", "Use Built-in Sample Dataset", "Connect SQL Database"],
        index=1
    )

    df = None
    dataset_name = "Sample Retail Dataset"

    if data_source == "Upload File (CSV/Excel)":
        uploaded_file = st.sidebar.file_uploader(
            "Upload Dataset",
            type=["csv", "xlsx", "xls"],
            help="Upload business dataset in CSV or Excel format"
        )
        if uploaded_file is not None:
            try:
                df = load_dataset(uploaded_file)
                dataset_name = uploaded_file.name
                st.sidebar.success(f"Loaded `{dataset_name}` ({len(df)} rows)")
            except Exception as e:
                st.sidebar.error(f"Error loading file: {str(e)}")

    elif data_source == "Use Built-in Sample Dataset":
        if os.path.exists(SAMPLE_CSV):
            df = pd.read_csv(SAMPLE_CSV)
            dataset_name = "retail_sales_sample.csv"
            st.sidebar.info("Using sample retail dataset with 26 transactions, sales, categories & profit.")
        else:
            st.sidebar.warning("Sample dataset file not found.")

    elif data_source == "Connect SQL Database":
        db_type = st.sidebar.selectbox("DB Engine", ["SQLite", "PostgreSQL", "MySQL"])
        if db_type == "SQLite":
            db_file = st.sidebar.text_input("Database File Path", value=os.path.join(os.path.dirname(__file__), "..", "dashboard_history.db"))
            if st.sidebar.button("Connect & Fetch Tables"):
                try:
                    engine = create_db_engine("SQLite", sqlite_path=db_file)
                    tables = list_tables(engine)
                    st.session_state["sql_tables"] = tables
                    st.session_state["sql_engine"] = engine
                    st.sidebar.success(f"Connected! Found {len(tables)} tables.")
                except Exception as e:
                    st.sidebar.error(f"Connection failed: {str(e)}")

        if "sql_tables" in st.session_state and st.session_state["sql_tables"]:
            selected_table = st.sidebar.selectbox("Select Table", st.session_state["sql_tables"])
            if st.sidebar.button("Load Table Data"):
                engine = st.session_state["sql_engine"]
                df = load_table_data(engine, selected_table)
                dataset_name = f"SQL Table: {selected_table}"
                st.sidebar.success(f"Loaded {selected_table} ({len(df)} rows)")

    st.sidebar.divider()
    st.sidebar.subheader("⚙️ Dashboard Settings")
    chart_theme = st.sidebar.selectbox("Chart Color Theme", ["plotly_dark", "plotly_white", "seaborn", "ggplot2"])
    
    st.sidebar.divider()
    st.sidebar.subheader("🤖 AI Engine Setup")
    llm_provider = st.sidebar.selectbox("AI Model Provider", ["Statistical Fallback (Built-in)", "OpenAI", "Ollama (Local)"])
    api_key = None
    if llm_provider == "OpenAI":
        api_key = st.sidebar.text_input("OpenAI API Key", type="password")

    llm_config = {
        "provider": llm_provider,
        "api_key": api_key,
        "theme": chart_theme
    }

    return df, dataset_name, llm_config
