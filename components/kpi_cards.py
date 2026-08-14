import streamlit as st
import numpy as np
import pandas as pd
from modules.data_processor import get_smart_column_mapping

def render_kpi_cards(df):
    """
    Computes key business metrics and renders responsive KPI metric cards.
    Returns: dict of calculated KPIs
    """
    mapping = get_smart_column_mapping(df)
    
    sales_col = mapping.get("sales")
    profit_col = mapping.get("profit")
    quantity_col = mapping.get("quantity")
    customer_col = mapping.get("customer")
    category_col = mapping.get("category")
    
    sales_series = pd.to_numeric(df[sales_col].astype(str).str.replace('$', '', regex=False).str.replace(',', '', regex=False), errors='coerce').fillna(0) if sales_col else None
    profit_series = pd.to_numeric(df[profit_col].astype(str).str.replace('$', '', regex=False).str.replace(',', '', regex=False), errors='coerce').fillna(0) if profit_col else None
    
    # Fallback to first non-id numerical column if sales_series is missing or 0
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    num_cols_no_id = [c for c in num_cols if not any(k in c.lower() for k in ['id', 'code', 'key', 'index', 'year'])]
    
    if (sales_series is None or sales_series.sum() == 0) and num_cols_no_id:
        fallback_col = num_cols_no_id[0]
        sales_series = pd.to_numeric(df[fallback_col], errors='coerce').fillna(0)
        sales_col = fallback_col

    if (profit_series is None or profit_series.sum() == 0) and sales_series is not None:
        if len(num_cols_no_id) > 1:
            fallback_prof = num_cols_no_id[1]
            profit_series = pd.to_numeric(df[fallback_prof], errors='coerce').fillna(0)
            profit_col = fallback_prof
        else:
            profit_series = sales_series * 0.25
            profit_col = "Derived (25%)"

    total_sales = sales_series.sum() if sales_series is not None else 0
    total_profit = profit_series.sum() if profit_series is not None else 0
    total_orders = len(df)
    
    profit_margin = (total_profit / total_sales * 100) if (sales_col and profit_col and total_sales > 0) else 0
    avg_order_val = (total_sales / total_orders) if (sales_col and total_orders > 0) else 0
    total_customers = df[customer_col].nunique() if customer_col else (df[category_col].nunique() if category_col else total_orders)


    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">💰 Total Sales</div>
            <div class="metric-value">${total_sales:,.2f}</div>
            <div class="metric-subtitle">Across {total_orders:,} orders</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        profit_color = "#10B981" if total_profit >= 0 else "#EF4444"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">📈 Net Profit</div>
            <div class="metric-value" style="color: {profit_color};">${total_profit:,.2f}</div>
            <div class="metric-subtitle">Margin: {profit_margin:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">🛒 Avg Order Value</div>
            <div class="metric-value">${avg_order_val:,.2f}</div>
            <div class="metric-subtitle">Per transaction</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">👥 Customers / Entities</div>
            <div class="metric-value">{total_customers:,}</div>
            <div class="metric-subtitle">Unique records</div>
        </div>
        """, unsafe_allow_html=True)

    with col5:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">📊 Dataset Size</div>
            <div class="metric-value">{len(df):,}</div>
            <div class="metric-subtitle">{len(df.columns)} Columns</div>
        </div>
        """, unsafe_allow_html=True)

    kpis = {
        "Total Sales": f"${total_sales:,.2f}" if sales_col else "N/A",
        "Net Profit": f"${total_profit:,.2f}" if profit_col else "N/A",
        "Profit Margin": f"{profit_margin:.1f}%" if sales_col and profit_col else "N/A",
        "Average Order Value": f"${avg_order_val:,.2f}" if sales_col else "N/A",
        "Total Orders": f"{total_orders:,}",
        "Unique Customers/Entities": f"{total_customers:,}"
    }

    return kpis
