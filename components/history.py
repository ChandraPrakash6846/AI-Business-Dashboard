import streamlit as st
import pandas as pd
from modules.database import fetch_history, fetch_query_history, clear_history

def render_history_tab():
    """
    Renders the Analysis History & Session Log viewer.
    """
    st.subheader("📜 Session Analysis History & Query Logs")
    st.caption("All dataset imports, KPI calculations, and natural language questions are logged in your local SQLite database.")

    col1, col2 = st.columns([4, 1])
    with col2:
        if st.button("🗑️ Clear History", type="secondary"):
            clear_history()
            st.success("History cleared successfully!")
            st.rerun()

    tab1, tab2 = st.tabs(["📁 Past Dataset Analysis", "💬 Natural Language Queries"])

    with tab1:
        history_records = fetch_history(limit=15)
        if history_records:
            for rec in history_records:
                with st.expander(f"📌 {rec['filename']} — {rec['timestamp']} ({rec['row_count']} rows, {rec['col_count']} cols)"):
                    st.write("**KPI Summary:**")
                    st.json(rec['kpis'])
                    st.write("**Data Health Summary:**")
                    st.json(rec['summary'])
        else:
            st.info("No past dataset analysis recorded yet.")

    with tab2:
        query_records = fetch_query_history(limit=25)
        if query_records:
            q_df = pd.DataFrame(query_records)
            st.dataframe(q_df[["timestamp", "query", "result"]], use_container_width=True)
        else:
            st.info("No natural language queries logged yet.")
