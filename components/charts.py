# AI Business Dashboard - Fully Updated & Verified
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from modules.data_processor import get_smart_column_mapping

def render_interactive_charts(df, theme="plotly_dark"):
    """
    Renders customizable interactive Plotly charts dashboard tab.
    """
    px.defaults.template = theme
    mapping = get_smart_column_mapping(df)
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    cat_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    date_cols = [c for c in df.columns if pd.api.types.is_datetime64_any_dtype(df[c])]

    st.subheader("📊 Interactive Dashboard Controls")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        chart_type = st.selectbox("Chart Type", ["Bar Chart", "Line Chart (Time Series)", "Pie / Donut Chart", "Scatter Plot", "Box Plot"], index=0)
    with col2:
        x_default = date_cols[0] if (chart_type == "Line Chart (Time Series)" and date_cols) else (cat_cols[0] if cat_cols else (df.columns[0]))
        x_axis = st.selectbox("X-Axis / Category Column", df.columns, index=list(df.columns).index(x_default) if x_default in df.columns else 0)
    with col3:
        y_default = mapping.get("sales") or (num_cols[0] if num_cols else df.columns[0])
        y_axis = st.selectbox("Y-Axis / Value Metric", num_cols if num_cols else df.columns, index=num_cols.index(y_default) if y_default in num_cols else 0)
    with col4:
        color_by = st.selectbox("Color / Group By (Optional)", ["None"] + cat_cols)
    with col5:
        top_n = st.selectbox("Top N Items", [10, 15, 20, 30, "Show All"], index=1)
        
    color_col = None if color_by == "None" else color_by

    st.divider()

    fig = None
    if chart_type == "Bar Chart":
        if color_col:
            agg_df = df.groupby([x_axis, color_col])[y_axis].sum().reset_index()
            if top_n != "Show All":
                top_cats = agg_df.groupby(x_axis)[y_axis].sum().nlargest(int(top_n)).index
                agg_df = agg_df[agg_df[x_axis].isin(top_cats)]
            fig = px.bar(agg_df, x=x_axis, y=y_axis, color=color_col, barmode="group",
                         title=f"Total {y_axis} by {x_axis} (Top {top_n} Grouped by {color_col})", template=theme)
        else:
            agg_df = df.groupby(x_axis)[y_axis].sum().sort_values(ascending=False).reset_index()
            if top_n != "Show All":
                agg_df = agg_df.head(int(top_n))
            fig = px.bar(agg_df, x=x_axis, y=y_axis, color=y_axis,
                         color_continuous_scale="Viridis",
                         title=f"Total {y_axis} by {x_axis} (Top {top_n})", template=theme)

    elif chart_type == "Line Chart (Time Series)":
        if pd.api.types.is_datetime64_any_dtype(df[x_axis]):
            df_sorted = df.sort_values(by=x_axis)
            if color_col:
                fig = px.line(df_sorted, x=x_axis, y=y_axis, color=color_col,
                              title=f"{y_axis} Trend Over Time by {color_col}", template=theme)
            else:
                fig = px.line(df_sorted, x=x_axis, y=y_axis, markers=True,
                              title=f"{y_axis} Trend Over Time", template=theme)
        else:
            st.warning("Selected X-Axis is not a Date column. Treating as category index.")
            fig = px.line(df, x=x_axis, y=y_axis, color=color_col, title=f"{y_axis} by {x_axis}", template=theme)

    elif chart_type == "Pie / Donut Chart":
        agg_df = df.groupby(x_axis)[y_axis].sum().sort_values(ascending=False).reset_index()
        if top_n != "Show All":
            agg_df = agg_df.head(int(top_n))
        fig = px.pie(agg_df, names=x_axis, values=y_axis, hole=0.4,
                     title=f"Distribution Share of {y_axis} by {x_axis} (Top {top_n})", template=theme)

    elif chart_type == "Scatter Plot":
        if len(num_cols) < 2:
            st.error("Scatter plot requires at least 2 numerical columns.")
        else:
            y2_axis = st.selectbox("Select Second Numeric Metric for Y-Axis", num_cols, index=num_cols.index(mapping.get("profit")) if mapping.get("profit") in num_cols else 0)
            fig = px.scatter(df, x=y_axis, y=y2_axis, color=color_col, size=mapping.get("quantity") if mapping.get("quantity") in df.columns else None,
                             hover_data=df.columns, title=f"Scatter Analysis: {y_axis} vs {y2_axis}", template=theme)

    elif chart_type == "Box Plot":
        fig = px.box(df, x=x_axis if cat_cols else None, y=y_axis, color=color_col,
                     title=f"Distribution & Outlier Box Plot of {y_axis}", template=theme)

    if fig is not None:
        fig.update_xaxes(tickangle=-45)
        fig.update_layout(height=520, template=theme, margin=dict(l=40, r=40, t=60, b=100))
        st.plotly_chart(fig, use_container_width=True)

