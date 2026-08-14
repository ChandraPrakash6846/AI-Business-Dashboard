import pandas as pd
import numpy as np
import requests
import json
import re
from sklearn.ensemble import IsolationForest
from modules.data_processor import get_smart_column_mapping

def generate_statistical_insights(df):
    """
    Generates rule-based and statistical business insights based on dataset analysis.
    """
    insights = []
    mapping = get_smart_column_mapping(df)
    
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    cat_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    date_cols = [c for c in df.columns if pd.api.types.is_datetime64_any_dtype(df[c])]
    
    # 1. Overall Revenue / Sales performance
    sales_col = mapping.get("sales")
    profit_col = mapping.get("profit")
    category_col = mapping.get("category")
    region_col = mapping.get("region")
    
    if sales_col:
        # Coerce to numeric in case column is string/object
        s_series = pd.to_numeric(df[sales_col].astype(str).str.replace('$', '', regex=False).str.replace(',', '', regex=False), errors='coerce').fillna(0)
        total_sales = s_series.sum()
        avg_sales = s_series.mean()
        
        insights.append({
            "type": "positive",
            "title": f"Total {sales_col.title()} Generated",
            "description": f"The dataset records a total cumulative {sales_col} of **${total_sales:,.2f}** with an average transaction value of **${avg_sales:,.2f}**."
        })
        
        if category_col and total_sales > 0:
            df_temp = df.copy()
            df_temp['_sales_num'] = s_series
            cat_perf = df_temp.groupby(category_col)['_sales_num'].sum().sort_values(ascending=False)
            if not cat_perf.empty:
                top_cat = cat_perf.index[0]
                top_cat_val = cat_perf.iloc[0]
                top_cat_pct = (top_cat_val / total_sales) * 100
                
                insights.append({
                    "type": "info",
                    "title": f"Top Performing Category: {top_cat}",
                    "description": f"**{top_cat}** leads sales generation with **${top_cat_val:,.2f}**, contributing **{top_cat_pct:.1f}%** of overall volume."
                })
            
    # 2. Profitability & Margin Analysis
    if profit_col:
        p_series = pd.to_numeric(df[profit_col].astype(str).str.replace('$', '', regex=False).str.replace(',', '', regex=False), errors='coerce').fillna(0)
        total_profit = p_series.sum()
        negative_profit = df[p_series < 0]
        
        if total_profit > 0:
            insights.append({
                "type": "positive",
                "title": "Net Profitability Status",
                "description": f"Overall business net profit is positive at **${total_profit:,.2f}**."
            })
        else:
            insights.append({
                "type": "warning",
                "title": "Unprofitable Operations Alert",
                "description": f"Overall net profit is negative (**${total_profit:,.2f}**). Immediate cost restructuring is recommended."
            })

            
        if not negative_profit.empty:
            loss_pct = (len(negative_profit) / len(df)) * 100
            insights.append({
                "type": "warning",
                "title": "Loss-Making Transactions Identified",
                "description": f"**{len(negative_profit)}** transactions (**{loss_pct:.1f}%** of total) operated at a loss. Review discounts and overhead allocation."
            })

    # 3. Region Analysis
    if region_col and sales_col:
        region_perf = df.groupby(region_col)[sales_col].sum().sort_values(ascending=False)
        top_region = region_perf.index[0]
        lowest_region = region_perf.index[-1]
        
        insights.append({
            "type": "info",
            "title": f"Regional Benchmark: {top_region}",
            "description": f"**{top_region}** is your strongest territory (**${region_perf.iloc[0]:,.2f}**), while **{lowest_region}** presents growth opportunities (**${region_perf.iloc[-1]:,.2f}**)."
        })

    # 4. Correlation Alert
    if len(num_cols) >= 2:
        corr_matrix = df[num_cols].corr().abs()
        corr_vals = corr_matrix.to_numpy(copy=True)
        np.fill_diagonal(corr_vals, 0)
        max_corr_val = corr_vals.max()
        if max_corr_val > 0.7:
            pair = corr_matrix.stack().idxmax()
            insights.append({
                "type": "info",
                "title": f"Strong Correlation Detected: {pair[0]} & {pair[1]}",
                "description": f"High statistical correlation coefficient (**{max_corr_val:.2f}**) found between **{pair[0]}** and **{pair[1]}**."
            })


    return insights

def detect_anomalies(df):
    """
    Detects unusual rows/anomalies in numeric columns using Isolation Forest.
    """
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if not num_cols:
        return df, []
        
    df_clean = df[num_cols].fillna(df[num_cols].median())
    
    model = IsolationForest(contamination=0.05, random_state=42)
    df_result = df.copy()
    df_result['is_anomaly'] = model.fit_predict(df_clean) == -1
    
    anomalies = df_result[df_result['is_anomaly']]
    return df_result, anomalies

def process_natural_language_query(query, df):
    """
    Parses natural language user queries and returns:
    1. Filtered or aggregated DataFrame
    2. Suggested chart type (bar, line, pie, scatter)
    3. Natural language summary answer
    """
    q = query.lower().strip()
    mapping = get_smart_column_mapping(df)
    
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    cat_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    date_cols = [c for c in df.columns if pd.api.types.is_datetime64_any_dtype(df[c])]
    
    res_df = df.copy()
    chart_type = "bar"
    summary = ""
    
    # Check category filter
    for cat in cat_cols:
        unique_vals = df[cat].dropna().unique()
        for u in unique_vals:
            if str(u).lower() in q:
                res_df = res_df[res_df[cat].astype(str).str.lower() == str(u).lower()]
                summary += f"Filtered for `{cat}` = **{u}**. "
                
    # Detect aggregation target
    target_metric = None
    for col in num_cols:
        if col.lower() in q:
            target_metric = col
            break
    if not target_metric:
        target_metric = mapping.get("sales") or (num_cols[0] if num_cols else None)

    # Detect grouping target
    group_col = None
    if "by category" in q or "per category" in q:
        group_col = mapping.get("category") or (cat_cols[0] if cat_cols else None)
    elif "by region" in q or "per region" in q or "by location" in q:
        group_col = mapping.get("region") or (cat_cols[1] if len(cat_cols) > 1 else cat_cols[0])
    elif "by customer" in q or "top customer" in q:
        group_col = mapping.get("customer") or (cat_cols[0] if cat_cols else None)
    elif "over time" in q or "trend" in q or "monthly" in q or "daily" in q:
        group_col = mapping.get("date") or (date_cols[0] if date_cols else None)
        chart_type = "line"
    else:
        # Default group by category or first categorical column if present
        for c in cat_cols:
            if c.lower() in q:
                group_col = c
                break

    # Top N queries
    top_n_match = re.search(r'top\s+(\d+)', q)
    limit_n = int(top_n_match.group(1)) if top_n_match else None

    if group_col and target_metric:
        if pd.api.types.is_datetime64_any_dtype(res_df[group_col]):
            agg_df = res_df.groupby(res_df[group_col].dt.to_period('M'))[target_metric].sum().reset_index()
            agg_df[group_col] = agg_df[group_col].astype(str)
        else:
            agg_df = res_df.groupby(group_col)[target_metric].sum().reset_index()
            
        agg_df = agg_df.sort_values(by=target_metric, ascending=False)
        if limit_n:
            agg_df = agg_df.head(limit_n)
            summary += f"Showing top {limit_n} `{group_col}` by total `{target_metric}`. "
        else:
            summary += f"Grouped total `{target_metric}` by `{group_col}`. "
            
        total_val = agg_df[target_metric].sum()
        top_item = agg_df.iloc[0][group_col]
        top_val = agg_df.iloc[0][target_metric]
        
        summary += f"Highest `{group_col}` is **{top_item}** with **${top_val:,.2f}** ({target_metric}). Total: **${total_val:,.2f}**."
        return agg_df, chart_type, summary, group_col, target_metric

    # Single aggregation query (e.g., "what is total profit?")
    if target_metric:
        if "highest" in q or "max" in q:
            val = res_df[target_metric].max()
            summary += f"The maximum `{target_metric}` is **${val:,.2f}**."
        elif "lowest" in q or "min" in q:
            val = res_df[target_metric].min()
            summary += f"The minimum `{target_metric}` is **${val:,.2f}**."
        elif "average" in q or "mean" in q or "avg" in q:
            val = res_df[target_metric].mean()
            summary += f"The average `{target_metric}` is **${val:,.2f}**."
        else:
            val = res_df[target_metric].sum()
            summary += f"The total sum of `{target_metric}` is **${val:,.2f}**."
        return res_df.head(20), "bar", summary, None, target_metric

    summary = f"Displayed top matching dataset records ({len(res_df)} rows found)."
    return res_df.head(20), "table", summary, None, None

def query_llm_api(prompt, api_provider="OpenAI", api_key=None):
    """
    Optional LLM integration for custom external API prompts (OpenAI / Gemini / Ollama).
    """
    if not api_key and api_provider in ["OpenAI", "Gemini"]:
        return "API Key is required for LLM integration. Please enter your API key in the sidebar."
        
    try:
        if api_provider == "OpenAI":
            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
            payload = {
                "model": "gpt-3.5-turbo",
                "messages": [{"role": "system", "content": "You are an expert AI business analyst."},
                             {"role": "user", "content": prompt}],
                "temperature": 0.3
            }
            resp = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload, timeout=10)
            if resp.status_code == 200:
                return resp.json()["choices"][0]["message"]["content"]
            else:
                return f"OpenAI API Error: {resp.text}"

        elif api_provider == "Ollama":
            payload = {"model": "llama2", "prompt": prompt, "stream": False}
            resp = requests.post("http://localhost:11434/api/generate", json=payload, timeout=10)
            if resp.status_code == 200:
                return resp.json().get("response", "No response from Ollama.")
            else:
                return "Ollama API error. Is Ollama running on http://localhost:11434?"
    except Exception as e:
        return f"LLM execution error: {str(e)}"

    return "LLM integration ready."
