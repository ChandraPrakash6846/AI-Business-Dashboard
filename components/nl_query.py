# AI Business Dashboard - Fully Updated & Verified
import streamlit as st
import plotly.express as px
import pandas as pd
from modules.ai_engine import process_natural_language_query, query_llm_api
from modules.database import save_nl_query

def render_nl_query_engine(df, llm_config):
    """
    Renders Natural Language Query interface.
    """
    px.defaults.template = llm_config.get("theme", "plotly_dark")
    st.subheader("🤖 Natural Language Data Query Assistant")

    st.caption("Ask questions about your business dataset in plain English (e.g., *'Total sales by category'*, *'Which region generated highest profit?'*, *'Show sales over time'*).")

    # Preset sample query buttons
    st.write("**Quick Example Queries:**")
    q_cols = st.columns(4)
    preset_query = None
    with q_cols[0]:
        if st.button("📊 Total sales by category"):
            preset_query = "Total sales by category"
    with q_cols[1]:
        if st.button("🏆 Top 5 sales records"):
            preset_query = "Top 5 sales"
    with q_cols[2]:
        if st.button("🌍 Profit by region"):
            preset_query = "Profit by region"
    with q_cols[3]:
        if st.button("📈 Sales over time"):
            preset_query = "Sales over time"

    query_input = st.text_input(
        "Enter your query:",
        value=preset_query if preset_query else "",
        placeholder="Type a question e.g. What is the total profit for Technology?"
    )

    if st.button("🚀 Ask Assistant", type="primary") or query_input:
        if not query_input:
            st.warning("Please type a query or click one of the quick options.")
            return

        with st.spinner("Processing natural language query..."):
            res_df, chart_type, summary, group_col, target_metric = process_natural_language_query(query_input, df)
            
            # Save query to database history
            save_nl_query(query_input, summary)

            st.markdown(f"### 💡 Answer & Summary\n{summary}")
            
            if group_col and target_metric and not res_df.empty:
                st.markdown("#### 📊 Dynamic Chart Generated")
                theme = llm_config.get("theme", "plotly_dark")
                if chart_type == "line":
                    fig = px.line(res_df, x=group_col, y=target_metric, markers=True,
                                  title=f"{target_metric} by {group_col}", template=theme)
                else:
                    fig = px.bar(res_df, x=group_col, y=target_metric, color=target_metric,
                                 color_continuous_scale="Viridis",
                                 title=f"{target_metric} by {group_col}", template=theme)
                st.plotly_chart(fig, use_container_width=True)

            st.markdown("#### 📄 Filtered Data Table")
            st.dataframe(res_df, use_container_width=True)

            # If LLM API provider selected
            if llm_config.get("provider") != "Statistical Fallback (Built-in)":
                st.divider()
                st.markdown("#### 🤖 LLM Executive Explanation")
                prompt = f"Dataset Summary:\n{df.describe().to_string()}\n\nUser Question: {query_input}\nParsed Summary: {summary}\nProvide a 2-paragraph executive commentary on these findings."
                llm_response = query_llm_api(prompt, llm_config.get("provider"), llm_config.get("api_key"))
                st.markdown(f"> {llm_response}")
