# AI Business Dashboard - Fully Updated & Verified
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
        ["Upload File(s) (CSV/Excel/SQL)", "Use Built-in Sample Dataset", "Connect SQL Database"],
        index=0
    )


    df = None
    dataset_name = "Sample Retail Dataset"

    if data_source == "Upload File(s) (CSV/Excel/SQL)":
        uploaded_files = st.sidebar.file_uploader(
            "Upload Dataset(s)",
            accept_multiple_files=True,
            help="Select all files together (Ctrl+A or drag box) - CSV, Excel, .sql script, or .db files supported"
        )


        if uploaded_files:
            if len(uploaded_files) == 1:
                try:
                    df = load_dataset(uploaded_files[0])
                    dataset_name = uploaded_files[0].name
                    st.sidebar.success(f"Loaded `{dataset_name}` ({len(df)} rows)")
                except Exception as e:
                    st.sidebar.error(f"Error loading file: {str(e)}")
            else:
                st.sidebar.info(f"📁 {len(uploaded_files)} files uploaded.")
                
                # Active File Selection vs Merged Analysis
                file_options = ["Merged / Combined Dataset"] + [f.name for f in uploaded_files]
                active_selection = st.sidebar.selectbox("Active Analysis View", file_options, index=0)
                
                if active_selection != "Merged / Combined Dataset":
                    target_file = next(f for f in uploaded_files if f.name == active_selection)
                    try:
                        df = load_dataset(target_file)
                        dataset_name = target_file.name
                        st.sidebar.success(f"Viewing `{dataset_name}` ({len(df)} rows)")
                    except Exception as e:
                        st.sidebar.error(f"Error loading {target_file.name}: {str(e)}")
                else:
                    combine_mode = st.sidebar.radio(
                        "Multi-File Strategy",
                        ["Smart Relational Join (Primary/Foreign Keys)", "Concatenate / Stack Rows"],
                        index=0
                    )
                    mode_key = "join" if "Relational" in combine_mode else "concat"
                    join_key = None
                    if mode_key == "join":
                        join_key_input = st.sidebar.text_input("Join Key Column", placeholder="e.g. orderNumber, customerNumber (blank = auto)")
                        join_key = join_key_input.strip() if join_key_input else None
                    
                    try:
                        from modules.data_processor import merge_multiple_datasets
                        df = merge_multiple_datasets(uploaded_files, mode=mode_key, join_key=join_key)
                        dataset_name = f"Smart Relational Joined ({len(uploaded_files)} Files: {', '.join([f.name for f in uploaded_files[:2]])}...)"
                        st.sidebar.success(f"Smart Joined {len(uploaded_files)} files ➔ {len(df)} rows")
                    except Exception as e:
                        st.sidebar.error(f"Multi-file join error: {str(e)}")




    elif data_source == "Use Built-in Sample Dataset":

        if os.path.exists(SAMPLE_CSV):
            df = pd.read_csv(SAMPLE_CSV)
            dataset_name = "retail_sales_sample.csv"
            st.sidebar.info("Using sample retail dataset with 26 transactions, sales, categories & profit.")
        else:
            st.sidebar.warning("Sample dataset file not found.")

    elif data_source == "Connect SQL Database":
        sql_mode = st.sidebar.radio(
            "SQL Connection Mode",
            ["Local SQLite Database or .sql Script", "Remote MySQL / PostgreSQL Server"],
            index=0
        )

        if sql_mode == "Local SQLite Database or .sql Script":
            uploaded_dbs = st.sidebar.file_uploader(
                "Upload .db, .sqlite or .sql Script File(s)",
                accept_multiple_files=True,
                help="Select all .sql or .db files together (Ctrl+A or drag box)"
            )

            default_db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "dashboard_history.db")).replace('\\', '/')
            db_file_path = st.sidebar.text_input("Or Enter Database / .sql File Path", value=default_db_path)
            
            if uploaded_dbs or st.sidebar.button("Connect & Load SQL Database(s)", type="primary"):
                try:
                    from modules.sql_connector import execute_sql_dump_script, list_tables, load_table_data
                    from modules.data_processor import merge_multiple_datasets

                    temp_db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "imported_sql_dump.db")).replace('\\', '/')
                    
                    if uploaded_dbs and len(uploaded_dbs) > 0:
                        engine = create_db_engine("SQLite", sqlite_path=temp_db_path)
                        for uploaded_db in uploaded_dbs:
                            fname = uploaded_db.name.lower()
                            if fname.endswith(".sql"):
                                sql_text = uploaded_db.getvalue().decode("utf-8", errors="ignore")
                                engine = execute_sql_dump_script(sql_text, temp_db_path)
                            else:
                                temp_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", f"uploaded_{uploaded_db.name}")).replace('\\', '/')
                                with open(temp_file, "wb") as f_out:
                                    f_out.write(uploaded_db.getbuffer())
                                engine = create_db_engine("SQLite", sqlite_path=temp_file)
                    else:
                        if db_file_path.lower().endswith(".sql") and os.path.exists(db_file_path):
                            with open(db_file_path, "r", encoding="utf-8", errors="ignore") as f_in:
                                sql_text = f_in.read()
                            engine = execute_sql_dump_script(sql_text, temp_db_path)
                        else:
                            engine = create_db_engine("SQLite", sqlite_path=db_file_path)

                    tables = list_tables(engine)
                    st.session_state["sql_tables"] = tables
                    st.session_state["sql_engine"] = engine

                    if tables:
                        table_dfs = [load_table_data(engine, t) for t in tables]
                        if len(tables) > 1:
                            df = merge_multiple_datasets(table_dfs, mode="join")
                            dataset_name = f"Smart Relational Joined ({len(tables)} SQL Tables)"
                            st.sidebar.success(f"Multi-SQL Joined {len(tables)} tables ➔ {len(df)} rows")
                        else:
                            df = table_dfs[0]
                            dataset_name = f"SQL Table: {tables[0]}"
                            st.sidebar.success(f"Loaded SQL Table `{tables[0]}` ({len(df)} rows)")

                except Exception as e:
                    st.sidebar.error(f"SQL Loading error: {str(e)}")

        elif sql_mode == "Remote MySQL / PostgreSQL Server":
            db_type = st.sidebar.selectbox("DB Engine", ["MySQL", "PostgreSQL"])
            default_port = 3306 if db_type == "MySQL" else 5432
            host = st.sidebar.text_input("Host", value="localhost")
            port = st.sidebar.number_input("Port", value=default_port, step=1)
            username = st.sidebar.text_input("Username", value="root")
            password = st.sidebar.text_input("Password", type="password")
            database = st.sidebar.text_input("Database Name", value="classicmodels")
            
            if st.sidebar.button(f"Connect to {db_type}", type="primary"):
                try:
                    engine = create_db_engine(db_type, host=host, port=port, database=database, username=username, password=password)
                    tables = list_tables(engine)
                    st.session_state["sql_tables"] = tables
                    st.session_state["sql_engine"] = engine
                    st.sidebar.success(f"Connected to {db_type}! Found {len(tables)} tables.")
                except Exception as e:
                    st.sidebar.error(f"{db_type} Connection error: {str(e)}")

        if "sql_tables" in st.session_state and st.session_state["sql_tables"]:
            tables = st.session_state["sql_tables"]
            engine = st.session_state.get("sql_engine")
            sql_view_options = ["Smart Relational Joined Multi-Table View (All Tables Auto-Joined)"] + tables if len(tables) > 1 else tables
            selected_table_option = st.sidebar.selectbox("Select Active SQL View", sql_view_options)
            
            if engine is not None:
                if selected_table_option != "Smart Relational Joined Multi-Table View (All Tables Auto-Joined)":
                    df = load_table_data(engine, selected_table_option)
                    dataset_name = f"SQL Table: {selected_table_option}"
                    st.sidebar.info(f"Active SQL Table: `{selected_table_option}` ({len(df)} rows)")
                elif df is None:
                    try:
                        from modules.data_processor import merge_multiple_datasets
                        table_dfs = [load_table_data(engine, t) for t in tables]
                        if len(table_dfs) > 1:
                            df = merge_multiple_datasets(table_dfs, mode="join")
                            dataset_name = f"Smart Relational Joined ({len(tables)} SQL Tables)"
                        elif len(table_dfs) == 1:
                            df = table_dfs[0]
                            dataset_name = f"SQL Table: {tables[0]}"
                    except Exception as e:
                        st.sidebar.error(f"Multi-Table Join error: {str(e)}")



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
