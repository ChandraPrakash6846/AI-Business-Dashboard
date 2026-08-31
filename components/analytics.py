# AI Business Dashboard - Fully Updated & Verified
import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np
from modules.ai_engine import detect_anomalies, generate_statistical_insights

def render_advanced_analytics(df, theme="plotly_dark"):
    """
    Renders correlation matrix, anomaly detection, and automated analytical insights.
    """
    px.defaults.template = theme
    st.subheader("🔍 Correlation, Trend & Anomaly Diagnostics")

    
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    tab1, tab2, tab3 = st.tabs(["🔥 Correlation Matrix", "🚨 Anomaly Detection (ML)", "💡 AI Executive Insights"])
    
    with tab1:
        st.markdown("#### Pearson Correlation Heatmap")
        if len(num_cols) >= 2:
            corr = df[num_cols].corr()
            fig = px.imshow(corr, text_auto=".2f", color_continuous_scale="RdBu_r",
                            title="Correlation Heatmap Across Numerical Factors", template=theme)
            st.plotly_chart(fig, use_container_width=True)
            
            st.info("💡 **Insight**: Correlation values close to +1.0 indicate strong positive alignment (e.g., Sales and Quantity), while negative values indicate opposing trends.")
        else:
            st.warning("At least 2 numerical columns are required for correlation matrix analysis.")

    with tab2:
        st.markdown("#### Machine Learning Anomaly Detection (Isolation Forest)")
        st.caption("Identifies potential fraud, data entry errors, or extreme business outliers.")
        
        if st.button("Run Isolation Forest Anomaly Scan"):
            df_result, anomalies = detect_anomalies(df)
            st.session_state["anomaly_results"] = (df_result, anomalies)
            
        if "anomaly_results" in st.session_state:
            df_result, anomalies = st.session_state["anomaly_results"]
            col_a, col_b = st.columns([1, 3])
            with col_a:
                st.metric("Detected Outlier Rows", len(anomalies), delta=f"{(len(anomalies)/len(df))*100:.1f}% of dataset", delta_color="inverse")
            with col_b:
                if not anomalies.empty:
                    st.dataframe(anomalies, height=200)
                else:
                    st.success("No significant statistical anomalies detected in this dataset.")
                    
            if len(num_cols) >= 2 and not anomalies.empty:
                fig = px.scatter(df_result, x=num_cols[0], y=num_cols[1] if len(num_cols) > 1 else num_cols[0],
                                 color=df_result['is_anomaly'].astype(str),
                                 color_discrete_map={"True": "#EF4444", "False": "#3B82F6"},
                                 title=f"Anomaly Visualizer: {num_cols[0]} vs {num_cols[1] if len(num_cols) > 1 else num_cols[0]}",
                                 template=theme)
                st.plotly_chart(fig, use_container_width=True)

    with tab3:
        st.markdown("#### Automatically Generated Strategic Recommendations")
        insights = generate_statistical_insights(df)
        
        for idx, item in enumerate(insights):
            card_class = f"insight-card insight-{item.get('type', 'info')}"
            st.markdown(f"""
            <div class="{card_class}">
                <strong style="font-size: 1.05rem;">{idx+1}. {item['title']}</strong><br/>
                <span style="color: #CBD5E1;">{item['description']}</span>
            </div>
            """, unsafe_allow_html=True)
