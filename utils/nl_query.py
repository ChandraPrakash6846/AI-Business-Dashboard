import pandas as pd
import numpy as np
import re
import plotly.express as px

def process_query(df, query):
    """Process a natural language query about the data."""
    try:
        q_lower = query.lower()
        
        # 1. Detect query type
        query_type = 'unknown'
        if any(w in q_lower for w in ['trend', 'over time', 'change', 'growth', 'timeline']):
            query_type = 'trend'
        elif any(w in q_lower for w in ['distribution', 'distributed', 'spread', 'histogram']):
            query_type = 'distribution'
        elif any(w in q_lower for w in ['compare', 'vs', 'versus', 'against', 'relationship']):
            query_type = 'comparison'
        elif any(w in q_lower for w in ['top', 'bottom', 'best', 'worst', 'highest', 'lowest', 'largest', 'smallest']):
            query_type = 'top_bottom'
        elif any(w in q_lower for w in ['by', 'per', 'each', 'across', 'group']):
            query_type = 'group_by'
        elif any(w in q_lower for w in ['where', 'for', 'in', 'only', 'filter']):
            query_type = 'filter'
        elif any(w in q_lower for w in ['total', 'sum', 'average', 'mean', 'max', 'maximum', 'min', 'minimum', 'count', 'how many']):
            query_type = 'aggregation'

        if query_type == 'unknown':
            pass # We will let it fall through to the general knowledge fallback at the end

        # Find columns
        num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        cat_cols = df.select_dtypes(exclude=[np.number]).columns.tolist()
        
        target_num_col = None
        for col in num_cols:
            if col.lower() in q_lower:
                target_num_col = col
                break
        if not target_num_col:
            target_num_col = _find_column(df, q_lower)
            if target_num_col and target_num_col not in num_cols:
                target_num_col = num_cols[0] if num_cols else None
                
        target_cat_col = _find_group_column(df, q_lower)

        # Process by type
        if query_type == 'aggregation':
            if any(w in q_lower for w in ['count', 'how many']):
                ans = f"There are {len(df)} records in total."
                return {'answer': ans, 'data': None, 'chart': None, 'success': True, 'query_type': query_type}
            
            if not target_num_col:
                target_num_col = num_cols[0] if num_cols else None
                
            if target_num_col:
                if any(w in q_lower for w in ['total', 'sum']):
                    val = df[target_num_col].sum()
                    ans = f"The total {target_num_col} is {val:,.2f}"
                elif any(w in q_lower for w in ['average', 'mean']):
                    val = df[target_num_col].mean()
                    ans = f"The average {target_num_col} is {val:,.2f}"
                elif any(w in q_lower for w in ['max', 'maximum', 'highest']):
                    val = df[target_num_col].max()
                    ans = f"The maximum {target_num_col} is {val:,.2f}"
                elif any(w in q_lower for w in ['min', 'minimum', 'lowest']):
                    val = df[target_num_col].min()
                    ans = f"The minimum {target_num_col} is {val:,.2f}"
                else:
                    val = df[target_num_col].sum()
                    ans = f"The total {target_num_col} is {val:,.2f}"
                return {'answer': ans, 'data': None, 'chart': None, 'success': True, 'query_type': query_type}

        elif query_type == 'group_by':
            if target_num_col and target_cat_col:
                agg_func = 'sum'
                if any(w in q_lower for w in ['average', 'mean']): agg_func = 'mean'
                elif any(w in q_lower for w in ['max', 'maximum']): agg_func = 'max'
                
                res_df = df.groupby(target_cat_col)[target_num_col].agg(agg_func).reset_index()
                fig = px.bar(res_df, x=target_cat_col, y=target_num_col, title=f"{target_num_col} by {target_cat_col}",
                             template='plotly_dark')
                fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                ans = f"Here is the {agg_func} of {target_num_col} grouped by {target_cat_col}."
                return {'answer': ans, 'data': res_df, 'chart': fig, 'success': True, 'query_type': query_type}

        elif query_type == 'top_bottom':
            if target_num_col and target_cat_col:
                n = 5
                match = re.search(r'\b(\d+)\b', q_lower)
                if match: n = int(match.group(1))
                
                is_bottom = any(w in q_lower for w in ['bottom', 'worst', 'lowest', 'smallest'])
                
                res_df = df.groupby(target_cat_col)[target_num_col].sum().reset_index()
                if is_bottom:
                    res_df = res_df.nsmallest(n, target_num_col)
                    word = "Bottom"
                else:
                    res_df = res_df.nlargest(n, target_num_col)
                    word = "Top"
                
                fig = px.bar(res_df, x=target_cat_col, y=target_num_col, title=f"{word} {n} {target_cat_col} by {target_num_col}",
                             template='plotly_dark')
                fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                ans = f"Here are the {word.lower()} {n} {target_cat_col} based on {target_num_col}."
                return {'answer': ans, 'data': res_df, 'chart': fig, 'success': True, 'query_type': query_type}

        elif query_type == 'trend':
            date_cols = df.select_dtypes(include=['datetime64', 'object']).columns.tolist()
            # rudimentary date col finding
            target_date_col = None
            for col in date_cols:
                if 'date' in col.lower() or 'time' in col.lower() or 'year' in col.lower() or 'month' in col.lower():
                    target_date_col = col
                    break
            if not target_date_col and cat_cols:
                target_date_col = cat_cols[0]
                
            if target_num_col and target_date_col:
                try:
                    df_temp = df.copy()
                    df_temp[target_date_col] = pd.to_datetime(df_temp[target_date_col])
                    res_df = df_temp.groupby(target_date_col)[target_num_col].sum().reset_index()
                    fig = px.line(res_df, x=target_date_col, y=target_num_col, title=f"{target_num_col} Trend over {target_date_col}",
                                  template='plotly_dark')
                    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                    return {'answer': f"Showing the trend of {target_num_col} over {target_date_col}.", 'data': res_df, 'chart': fig, 'success': True, 'query_type': query_type}
                except:
                    pass

        elif query_type == 'distribution':
            if target_num_col:
                fig = px.histogram(df, x=target_num_col, title=f"Distribution of {target_num_col}",
                                   template='plotly_dark')
                fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                return {'answer': f"Here is the distribution of {target_num_col}.", 'data': df[[target_num_col]], 'chart': fig, 'success': True, 'query_type': query_type}

        elif query_type == 'comparison':
            if target_num_col and target_cat_col:
                res_df = df.groupby(target_cat_col)[target_num_col].sum().reset_index()
                fig = px.bar(res_df, x=target_cat_col, y=target_num_col, title=f"Comparison of {target_num_col} across {target_cat_col}",
                             template='plotly_dark')
                fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                return {'answer': f"Comparing {target_num_col} across different {target_cat_col}.", 'data': res_df, 'chart': fig, 'success': True, 'query_type': query_type}

        elif query_type == 'filter':
            if target_cat_col:
                # Find the value to filter by
                unique_vals = df[target_cat_col].dropna().astype(str).unique()
                filter_val = None
                for val in unique_vals:
                    if val.lower() in q_lower:
                        filter_val = val
                        break
                if filter_val:
                    res_df = df[df[target_cat_col].astype(str).str.lower() == filter_val.lower()]
                    ans = f"Filtered data where {target_cat_col} is {filter_val}."
                    return {'answer': ans, 'data': res_df.head(100), 'chart': None, 'success': True, 'query_type': query_type}

        # Fallback if nothing specific was matched but we have a num col
        if target_num_col:
            val = df[target_num_col].sum()
            ans = f"Based on your query, the total {target_num_col} is {val:,.2f}"
            return {'answer': ans, 'data': None, 'chart': None, 'success': True, 'query_type': 'aggregation'}
            
        # --- GENERAL KNOWLEDGE FALLBACK ---
        import urllib.request, urllib.parse, json
        
        # Try to use Wikipedia Search API instead of Page Summary to be more robust
        try:
            # Strip common question prefixes to get better search results
            search_query = query.lower()
            for prefix in ["what is the", "what is a", "what is", "who is the", "who is a", "who is", "tell me about", "define", "where is"]:
                if search_query.startswith(prefix):
                    search_query = search_query[len(prefix):].strip()
            search_query = search_query.strip(' ?.!').strip()
            
            if search_query:
                search_url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={urllib.parse.quote(search_query)}&utf8=&format=json"
                req = urllib.request.Request(search_url, headers={'User-Agent': 'Mozilla/5.0 AI-Dashboard/1.0'})
                with urllib.request.urlopen(req, timeout=5) as response:
                    data = json.loads(response.read().decode())
                    search_results = data.get('query', {}).get('search', [])
                    if search_results:
                        title = search_results[0]['title']
                        # Now get the summary for this exact title
                        sum_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(title.replace(' ', '_'))}"
                        req2 = urllib.request.Request(sum_url, headers={'User-Agent': 'Mozilla/5.0 AI-Dashboard/1.0'})
                        with urllib.request.urlopen(req2, timeout=5) as response2:
                            data2 = json.loads(response2.read().decode())
                            if 'extract' in data2:
                                return {
                                    'answer': f"📖 **Web Search ({data2.get('title', title)})**\n\n{data2['extract']}",
                                    'data': None, 'chart': None, 'success': True, 'query_type': 'general'
                                }
        except Exception as e:
            pass

        return {
            'answer': "I couldn't find relevant columns in your data to answer that, and no general information was found on the web.",
            'data': None, 'chart': None, 'success': False, 'query_type': query_type
        }
    except Exception as e:
        return {
            'answer': f"An error occurred while processing your query: {str(e)}",
            'data': None, 'chart': None, 'success': False, 'query_type': 'error'
        }

def _find_column(df, search_term):
    """Find the best matching column name from a search term."""
    search_term = search_term.lower()
    cols = df.columns.tolist()
    
    # Exact match
    for col in cols:
        if col.lower() in search_term:
            return col
            
    # Synonyms
    synonyms = {
        'sales': ['quantity', 'units_sold', 'units', 'amount'],
        'revenue': ['money', 'income', 'sales', 'total'],
        'profit': ['margin', 'earnings', 'net'],
        'cost': ['expense', 'spend', 'cogs'],
        'date': ['time', 'year', 'month', 'day', 'timestamp']
    }
    
    for term, syns in synonyms.items():
        if term in search_term:
            for col in cols:
                if col.lower() in syns or term in col.lower():
                    return col
    return None

def _find_group_column(df, query):
    """Find the categorical column to group by from the query."""
    query = query.lower()
    cat_cols = df.select_dtypes(exclude=[np.number]).columns.tolist()
    
    for col in cat_cols:
        if col.lower() in query:
            return col
            
    # Fallback to first categorical column if keywords like 'by', 'per' exist
    if any(w in query for w in ['by', 'per', 'across']) and cat_cols:
        return cat_cols[0]
        
    return None

def get_sample_queries(df):
    """Generate sample queries that work with the current dataset."""
    queries = []
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    cat_cols = df.select_dtypes(exclude=[np.number]).columns.tolist()
    
    if num_cols:
        num = num_cols[0]
        queries.append(f"What is the total {num}?")
        queries.append(f"What is the average {num}?")
        queries.append(f"Distribution of {num}")
        
    if num_cols and cat_cols:
        num = num_cols[0]
        cat = cat_cols[0]
        queries.append(f"Show {num} by {cat}")
        queries.append(f"Top 5 {cat} by {num}")
        queries.append(f"Compare {num} across {cat}")
        
    if not queries:
        queries = ["How many rows are there?"]
        
    return queries[:8]
