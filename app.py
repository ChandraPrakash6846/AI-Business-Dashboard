# AI Business Dashboard - Fully Updated & Verified
import streamlit as st
import pandas as pd
import numpy as np
import os

from config import apply_custom_styles
from components.sidebar import render_sidebar
from components.kpi_cards import render_kpi_cards
from components.charts import render_interactive_charts
from components.analytics import render_advanced_analytics
from components.nl_query import render_nl_query_engine
from components.history import render_history_tab

from modules.data_processor import clean_and_validate
from modules.ai_engine import generate_statistical_insights
from modules.export_engine import export_to_pdf, export_to_excel
from modules.database import save_analysis_history

# Page Configuration
st.set_page_config(
    page_title="AI Business Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    # Sidebar
    df_raw, dataset_name, llm_config = render_sidebar()

    # Apply CSS styling dynamically matching selected theme
    apply_custom_styles(llm_config.get("theme", "plotly_dark"))


    if df_raw is None:
        st.warning("⚠️ Please select or upload a dataset using the sidebar to begin.")
        return


    # Clean & validate dataset automatically
    df_cleaned, health_report = clean_and_validate(df_raw)
    insights = generate_statistical_insights(df_cleaned)

    # Top Header Banner
    st.markdown(f"""
    <div class="header-banner">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <h1 class="header-title">📊 AI Business Dashboard</h1>
                <div class="header-subtitle">Dataset Active: <strong>{dataset_name}</strong> • Auto-Cleaned: {health_report['original_rows']} Rows → {health_report['final_rows']} Rows ({health_report['duplicates_removed']} Duplicates Removed)</div>
            </div>
            <div style="background: rgba(37, 99, 235, 0.2); border: 1px solid #3B82F6; padding: 6px 14px; border-radius: 20px; text-align: right;">
                <span style="color: #60A5FA; font-weight: 700; font-size: 0.85rem;">🎓 INTERNSHIP CAPSTONE PROJECT</span><br/>
                <span style="color: #94A3B8; font-size: 0.75rem;">AI & Business Analytics Track</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


    # Compute KPIs
    kpis = render_kpi_cards(df_cleaned)

    # Save to history DB (once per load)
    if "current_dataset" not in st.session_state or st.session_state["current_dataset"] != dataset_name:
        save_analysis_history(
            filename=dataset_name,
            row_count=health_report["final_rows"],
            col_count=health_report["final_cols"],
            summary=health_report,
            insights=insights,
            kpis=kpis
        )
        st.session_state["current_dataset"] = dataset_name

    # Export Action Bar
    st.divider()
    exp_col1, exp_col2, exp_col3 = st.columns([3, 1, 1])
    with exp_col1:
        st.write("📄 **Export Reports:** Download executive PDF analysis or full Excel summary.")
    with exp_col2:
        pdf_data = export_to_pdf(df_cleaned, health_report, kpis, insights)
        st.download_button(
            label="📥 Download PDF Report",
            data=pdf_data,
            file_name=f"{dataset_name}_Report.pdf",
            mime="application/pdf"
        )
    with exp_col3:
        excel_data = export_to_excel(df_cleaned, health_report, kpis, insights)
        st.download_button(
            label="📥 Export Excel Report",
            data=excel_data,
            file_name=f"{dataset_name}_Export.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    st.divider()

    # Main Tabs Navigation
    tab_overview, tab_charts, tab_analytics, tab_nl, tab_history = st.tabs([
        "📊 Overview & Health",
        "📈 Interactive Visualizations",
        "🔍 Advanced Analytics & Anomalies",
        "🤖 Natural Language Queries",
        "📜 Analysis History"
    ])

    # Tab 1: Overview & Data Health
    with tab_overview:
        col_left, col_right = st.columns([3, 2])
        
        with col_left:
            st.subheader("📋 Cleaned Dataset Preview")
            st.dataframe(df_cleaned.head(50), use_container_width=True, height=400)

        with col_right:
            st.subheader("🩺 Automated Data Health Check")
            health_df = pd.DataFrame([
                {"Metric": "Original Rows", "Value": health_report["original_rows"]},
                {"Metric": "Final Cleaned Rows", "Value": health_report["final_rows"]},
                {"Metric": "Total Columns", "Value": health_report["final_cols"]},
                {"Metric": "Duplicates Removed", "Value": health_report["duplicates_removed"]},
                {"Metric": "Missing Values Imputed", "Value": health_report["missing_filled"]},
                {"Metric": "Date Columns Detected", "Value": len(health_report["date_cols_detected"])},
                {"Metric": "Numeric Columns", "Value": len(health_report["numeric_cols"])},
                {"Metric": "Categorical Columns", "Value": len(health_report["categorical_cols"])}
            ])
            st.dataframe(health_df, use_container_width=True, hide_index=True)
            
            st.markdown("#### 💡 Quick AI Data Summary")
            for item in insights[:2]:
                st.info(f"**{item['title']}**: {item['description']}")

    # Tab 2: Interactive Charts
    with tab_charts:
        render_interactive_charts(df_cleaned, theme=llm_config.get("theme", "plotly_dark"))

    # Tab 3: Advanced Analytics & Anomalies
    with tab_analytics:
        render_advanced_analytics(df_cleaned, theme=llm_config.get("theme", "plotly_dark"))

    # Tab 4: Natural Language Query Engine
    with tab_nl:
        render_nl_query_engine(df_cleaned, llm_config)

    # Tab 5: History Tab
    with tab_history:
        render_history_tab()

    # Professional Internship Footer
    st.markdown("""
    <hr style="border: 0; border-top: 1px solid rgba(255,255,255,0.1); margin-top: 40px; margin-bottom: 20px;"/>
    <div style="text-align: center; color: #64748B; font-size: 0.85rem; padding-bottom: 20px;">
        <p>🎓 <strong>Internship Assignment Project Submission</strong> • Developed for Evaluation</p>
        <p>Tech Stack: Python • Streamlit • Pandas • Plotly • Scikit-learn • SQLAlchemy • ReportLab</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()

