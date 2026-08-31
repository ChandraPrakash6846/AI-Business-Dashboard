import pandas as pd
import numpy as np

def clean_data(df):
    """Auto-clean and validate data. Returns (cleaned_df, report_dict).
    
    Steps:
    1. Remove exact duplicate rows. Record count removed.
    2. For numeric columns with missing values: fill with column median.
    3. For categorical/string columns with missing values: fill with mode (most frequent).
    4. Try to convert string columns that look like dates to datetime (use pd.to_datetime with errors='coerce', infer_datetime_format). 
    5. Strip whitespace from string columns.
    6. Detect outliers in numeric columns using IQR method (Q1 - 1.5*IQR, Q3 + 1.5*IQR). Don't remove them, just count them.
    
    Returns:
      - cleaned_df: pd.DataFrame
      - report: dict with keys:
        - 'duplicates_removed': int
        - 'missing_filled': dict of col -> count filled
        - 'types_converted': list of col names converted to datetime
        - 'outliers_detected': dict of col -> count of outliers
        - 'total_issues_fixed': int (sum of all fixes)
    """
    if df is None or df.empty:
        return pd.DataFrame(), {}
        
    try:
        cleaned_df = df.copy()
        report = {
            'duplicates_removed': 0,
            'missing_filled': {},
            'types_converted': [],
            'outliers_detected': {},
            'total_issues_fixed': 0
        }
        
        initial_rows = len(cleaned_df)
        cleaned_df = cleaned_df.drop_duplicates()
        report['duplicates_removed'] = initial_rows - len(cleaned_df)
        report['total_issues_fixed'] += report['duplicates_removed']
        
        numeric_cols = cleaned_df.select_dtypes(include=[np.number]).columns
        object_cols = cleaned_df.select_dtypes(include=['object', 'string', 'category']).columns
        
        for col in numeric_cols:
            missing_count = cleaned_df[col].isnull().sum()
            if missing_count > 0:
                median_val = cleaned_df[col].median()
                if pd.isna(median_val):
                    median_val = 0
                cleaned_df[col] = cleaned_df[col].fillna(median_val)
                report['missing_filled'][col] = int(missing_count)
                report['total_issues_fixed'] += int(missing_count)
                
        for col in object_cols:
            missing_count = cleaned_df[col].isnull().sum()
            if missing_count > 0:
                mode_s = cleaned_df[col].mode()
                mode_val = mode_s.iloc[0] if not mode_s.empty else 'Unknown'
                cleaned_df[col] = cleaned_df[col].fillna(mode_val)
                report['missing_filled'][col] = int(missing_count)
                report['total_issues_fixed'] += int(missing_count)
                
        for col in object_cols:
            if cleaned_df[col].dtype == 'object' or pd.api.types.is_string_dtype(cleaned_df[col]):
                try:
                    cleaned_df[col] = cleaned_df[col].astype(str).str.strip()
                    
                    import re
                    # Safely remove common currency symbols, commas, and spaces
                    cleaned_text = cleaned_df[col].astype(str).str.replace(r'[$,₹€£\s]|Rs\.?', '', regex=True, flags=re.IGNORECASE)
                    
                    # Convert empty strings to NaN before to_numeric
                    cleaned_text = cleaned_text.replace('', float('nan'))
                    
                    converted = pd.to_numeric(cleaned_text, errors='coerce')
                    
                    # Only convert if it's overwhelmingly numeric (e.g. > 80%)
                    if converted.notnull().mean() > 0.8:  
                        cleaned_df[col] = converted
                        median_val = cleaned_df[col].median()
                        cleaned_df[col] = cleaned_df[col].fillna(median_val if not pd.isna(median_val) else 0)
                        
                        # IMPORTANT: Re-evaluate numeric columns list so detect_kpi_columns sees them!
                        numeric_cols = cleaned_df.select_dtypes(include=[np.number]).columns
                except Exception:
                    pass
        for col in object_cols:
            sample = cleaned_df[col].dropna().head(10).astype(str)
            if len(sample) > 0 and sample.str.len().mean() < 30:
                try:
                    if sample.str.contains(r'[-/:]').any():
                        converted = pd.to_datetime(cleaned_df[col], errors='coerce', format='mixed')
                        if converted.notnull().mean() > 0.5:
                            cleaned_df[col] = converted
                            report['types_converted'].append(col)
                except Exception:
                    pass
                    
        for col in numeric_cols:
            q1 = cleaned_df[col].quantile(0.25)
            q3 = cleaned_df[col].quantile(0.75)
            iqr = q3 - q1
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr
            
            outliers = ((cleaned_df[col] < lower_bound) | (cleaned_df[col] > upper_bound)).sum()
            if outliers > 0:
                report['outliers_detected'][col] = int(outliers)
                
        return cleaned_df, report
        
    except Exception as e:
        print(f"Error in data_cleaner: {e}")
        return df, {}

def detect_column_types(df):
    """Detect semantic column types.
    Returns: dict with keys:
      - 'date_columns': list (datetime64 columns)
      - 'numeric_columns': list (int64, float64 columns)
      - 'categorical_columns': list (object, category columns)
    """
    if df is None or df.empty:
        return {'date_columns': [], 'numeric_columns': [], 'categorical_columns': []}
        
    try:
        return {
            'date_columns': df.select_dtypes(include=['datetime']).columns.tolist(),
            'numeric_columns': df.select_dtypes(include=[np.number]).columns.tolist(),
            'categorical_columns': df.select_dtypes(include=['object', 'category']).columns.tolist()
        }
    except Exception as e:
        print(f"Error detecting column types: {e}")
        return {'date_columns': [], 'numeric_columns': [], 'categorical_columns': []}
