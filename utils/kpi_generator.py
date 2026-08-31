import pandas as pd
import numpy as np

def detect_kpi_columns(df):
    """Auto-detect columns for KPIs based on column name matching.
    
    Match column names (case-insensitive) to these KPI types:
    - 'sales': matches 'sales', 'total_sales', 'units_sold', 'quantity'
    - 'revenue': matches 'revenue', 'total_revenue', 'income', 'amount'
    - 'profit': matches 'profit', 'net_profit', 'gross_profit', 'margin'
    - 'customers': matches 'customers', 'customer_count', 'clients', 'users'
    - 'cost': matches 'cost', 'total_cost', 'expense', 'expenses'
    - 'rating': matches 'rating', 'score', 'satisfaction'
    
    Only match numeric columns.
    
    Returns: dict mapping kpi_type -> column_name
    Example: {'sales': 'Quantity', 'revenue': 'Revenue', 'profit': 'Profit', 'customers': 'Customers'}
    """
    if df is None or df.empty:
        return {}
        
    kpi_mapping = {}
    try:
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        keywords = {
            'sales': ['sales', 'total_sales', 'units_sold', 'quantity'],
            'revenue': ['revenue', 'total_revenue', 'income', 'amount'],
            'profit': ['profit', 'net_profit', 'gross_profit', 'margin'],
            'customers': ['customers', 'customer_count', 'clients', 'users'],
            'cost': ['cost', 'total_cost', 'expense', 'expenses'],
            'rating': ['rating', 'score', 'satisfaction']
        }
        
        for kpi_type, words in keywords.items():
            for col in numeric_cols:
                col_lower = col.lower()
                if any(word in col_lower for word in words):
                    kpi_mapping[kpi_type] = col
                    break
                    
        # Always try to pad up to 4 KPIs if we have enough numeric columns
        if len(kpi_mapping) < 4 and len(numeric_cols) > 0:
            used_cols = set(kpi_mapping.values())
            for col in numeric_cols:
                if col not in used_cols:
                    # Give it a generic key based on column name
                    kpi_mapping[col.lower().replace(' ', '_')] = col
                    used_cols.add(col)
                if len(kpi_mapping) >= 4:
                    break

        return kpi_mapping
    except Exception as e:
        print(f"Error detecting KPI columns: {e}")
        return {}

def calculate_kpis(df, kpi_columns=None):
    """Calculate KPI metrics for display.
    
    If kpi_columns is None, call detect_kpi_columns(df) first.
    
    For each detected KPI column, calculate:
    - total (sum)
    - average (mean)
    - min and max
    - For delta: split data in half (first half vs second half by row order), 
      calculate percentage change = ((second_half_sum - first_half_sum) / first_half_sum * 100)
    
    Returns: list of dicts, each with:
      - 'name': str (e.g., 'Total Revenue')
      - 'value': float (the total/sum)
      - 'formatted_value': str (formatted with commas, e.g., '$1,234,567' for monetary, '1,234' for counts)
      - 'icon': str (emoji: 💰 for revenue, 📦 for sales, 💎 for profit, 👥 for customers, 💵 for cost, ⭐ for rating)
      - 'delta': float (percentage change)
      - 'delta_formatted': str (e.g., '+15.2%' or '-3.4%')
      - 'average': float
      - 'min_val': float
      - 'max_val': float
    """
    if df is None or df.empty:
        return []
        
    try:
        if kpi_columns is None:
            kpi_columns = detect_kpi_columns(df)
            
        icons = {
            'revenue': '💰',
            'sales': '📦',
            'profit': '💎',
            'customers': '👥',
            'cost': '💵',
            'rating': '⭐'
        }
        
        kpi_list = []
        n_rows = len(df)
        half_idx = n_rows // 2
        
        for kpi_type, col_name in kpi_columns.items():
            if col_name not in df.columns or not pd.api.types.is_numeric_dtype(df[col_name]):
                continue
                
            col_data = df[col_name].dropna()
            if len(col_data) == 0:
                continue
                
            total = float(col_data.sum())
            average = float(col_data.mean())
            min_val = float(col_data.min())
            max_val = float(col_data.max())
            
            delta = 0.0
            if n_rows >= 2:
                first_half = df[col_name].iloc[:half_idx].sum()
                second_half = df[col_name].iloc[half_idx:].sum()
                if first_half != 0:
                    delta = float(((second_half - first_half) / first_half) * 100)
            
            if kpi_type in ['revenue', 'profit', 'cost'] or any(m in col_name.lower() for m in ['price', 'cost', 'revenue', 'profit', 'amount']):
                formatted_value = f"${total:,.0f}"
                name_prefix = "Total "
            elif kpi_type == 'rating' or any(m in col_name.lower() for m in ['rating', 'score', 'satisfaction']):
                formatted_value = f"{average:,.1f}"
                name_prefix = "Average "
                total = average
            else:
                formatted_value = f"{total:,.0f}"
                name_prefix = "Total "
                
            # Use actual column name for the KPI card to match dataset exactly
            clean_col_name = str(col_name).replace('_', ' ').title()
            formatted_name = f"{name_prefix}{clean_col_name}"
            
            if delta > 0:
                delta_formatted = f"+{delta:.1f}%"
            elif delta < 0:
                delta_formatted = f"{delta:.1f}%"
            else:
                delta_formatted = "0.0%"
                
            kpi_list.append({
                'name': formatted_name,
                'value': total,
                'formatted_value': formatted_value,
                'icon': icons.get(kpi_type, '📊'),
                'delta': delta,
                'delta_formatted': delta_formatted,
                'average': average,
                'min_val': min_val,
                'max_val': max_val
            })
            
        return kpi_list
    except Exception as e:
        print(f"Error calculating KPIs: {e}")
        return []
