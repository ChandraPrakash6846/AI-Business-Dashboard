import pandas as pd
import numpy as np

def load_dataset(file_or_path):
    """
    Load dataset from file buffer or path. Supports CSV and Excel (.xlsx, .xls).
    """
    if isinstance(file_or_path, str):
        if file_or_path.endswith('.csv'):
            df = pd.read_csv(file_or_path)
        elif file_or_path.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(file_or_path)
        else:
            raise ValueError("Unsupported file format. Please upload CSV or Excel file.")
    else:
        filename = getattr(file_or_path, 'name', '').lower()
        if filename.endswith('.csv'):
            df = pd.read_csv(file_or_path)
        elif filename.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(file_or_path)
        else:
            # Fallback attempt
            try:
                df = pd.read_csv(file_or_path)
            except Exception:
                file_or_path.seek(0)
                df = pd.read_excel(file_or_path)
    return df

def clean_and_validate(df):
    """
    Automatically cleans data:
    1. Trims string columns
    2. Detects and parses dates
    3. Handles missing values
    4. Removes duplicate rows
    5. Returns cleaned dataframe and diagnostic health report
    """
    health_report = {
        "original_rows": len(df),
        "original_cols": len(df.columns),
        "duplicates_removed": 0,
        "missing_filled": 0,
        "date_cols_detected": [],
        "numeric_cols": [],
        "categorical_cols": []
    }
    
    cleaned_df = df.copy()
    
    # 1. Trim column names
    cleaned_df.columns = [str(col).strip() for col in cleaned_df.columns]
    
    # 2. Duplicate handling
    dup_count = cleaned_df.duplicated().sum()
    if dup_count > 0:
        cleaned_df = cleaned_df.drop_duplicates()
    health_report["duplicates_removed"] = int(dup_count)
    
    # 3. String trimming, Date & Numeric Detection
    for col in cleaned_df.columns:
        if cleaned_df[col].dtype == 'object':
            cleaned_df[col] = cleaned_df[col].astype(str).str.strip()
            
            # Check if column looks like dates
            if any(term in col.lower() for term in ['date', 'time', 'day', 'created', 'updated', 'month', 'year']):
                try:
                    converted = pd.to_datetime(cleaned_df[col], errors='coerce')
                    if converted.notnull().sum() > 0.5 * len(cleaned_df):
                        cleaned_df[col] = converted
                        health_report["date_cols_detected"].append(col)
                        continue
                except Exception:
                    pass
            
            # Attempt numeric conversion (stripping $, commas, %)
            clean_str = cleaned_df[col].str.replace('$', '', regex=False).str.replace(',', '', regex=False).str.replace('%', '', regex=False).str.strip()
            numeric_converted = pd.to_numeric(clean_str, errors='coerce')
            if numeric_converted.notnull().sum() > 0.5 * len(cleaned_df):
                cleaned_df[col] = numeric_converted

    # 4. Impute Missing Values
    missing_count = cleaned_df.isnull().sum().sum()
    health_report["missing_filled"] = int(missing_count)
    
    for col in cleaned_df.columns:
        if cleaned_df[col].isnull().sum() > 0:
            if pd.api.types.is_numeric_dtype(cleaned_df[col]):
                # Fill missing with median
                cleaned_df[col] = cleaned_df[col].fillna(cleaned_df[col].median())
            elif pd.api.types.is_datetime64_any_dtype(cleaned_df[col]):
                cleaned_df[col] = cleaned_df[col].bfill().ffill()
            else:
                # Categorical fill mode
                mode_val = cleaned_df[col].mode()
                fill_val = mode_val[0] if not mode_val.empty else "Unknown"
                cleaned_df[col] = cleaned_df[col].fillna(fill_val)

    # 5. Categorize Columns
    for col in cleaned_df.columns:
        if pd.api.types.is_numeric_dtype(cleaned_df[col]):
            health_report["numeric_cols"].append(col)
        elif not pd.api.types.is_datetime64_any_dtype(cleaned_df[col]):
            health_report["categorical_cols"].append(col)

    health_report["final_rows"] = len(cleaned_df)
    health_report["final_cols"] = len(cleaned_df.columns)

    return cleaned_df, health_report


def get_smart_column_mapping(df):
    """
    Identifies probability mapping of columns to business domains:
    sales, revenue, profit, cost, quantity, date, category, region, customer.
    """
    cols = df.columns
    cols_lower = [c.lower() for c in cols]
    
    def match(keywords):
        for kw in keywords:
            for i, c in enumerate(cols_lower):
                if kw in c:
                    return cols[i]
        return None

    mapping = {
        "sales": match(['sales', 'revenue', 'turnover', 'amount', 'total_amount', 'price']),
        "profit": match(['profit', 'margin', 'gain', 'net_income', 'earnings']),
        "quantity": match(['qty', 'quantity', 'count', 'units']),
        "date": match(['date', 'time', 'order_date', 'day', 'timestamp']),
        "category": match(['category', 'type', 'group', 'product_type', 'department']),
        "region": match(['region', 'country', 'state', 'city', 'location', 'zone']),
        "customer": match(['customer', 'client', 'user', 'buyer', 'customer_name'])
    }
    return mapping
