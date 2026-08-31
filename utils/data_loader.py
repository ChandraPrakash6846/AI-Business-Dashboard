import pandas as pd
import sqlite3
import io
import os
import tempfile

def load_file(uploaded_file):
    """Load CSV or Excel file into DataFrame.
    Args: uploaded_file - Streamlit UploadedFile object with .name attribute
    Returns: pd.DataFrame
    Handles: .csv, .xlsx, .xls files
    For CSV: try utf-8, then latin-1 encoding
    For Excel: read first sheet by default
    """
    if uploaded_file is None:
        return None
    
    file_name = uploaded_file.name.lower()
    
    try:
        if file_name.endswith('.csv'):
            try:
                return pd.read_csv(uploaded_file, encoding='utf-8')
            except UnicodeDecodeError:
                uploaded_file.seek(0)
                return pd.read_csv(uploaded_file, encoding='latin-1')
        elif file_name.endswith(('.xlsx', '.xls')):
            return pd.read_excel(uploaded_file)
        else:
            raise ValueError(f"Unsupported file extension: {file_name}")
    except Exception as e:
        print(f"Error loading file: {e}")
        return pd.DataFrame()

def load_sqlite_db(uploaded_file):
    """Load SQLite database file.
    Args: uploaded_file - Streamlit UploadedFile object (.db or .sqlite)
    Returns: dict mapping table_name -> pd.DataFrame
    Save file temporarily, connect with sqlite3, read all tables.
    """
    if uploaded_file is None:
        return {}
        
    db_dict = {}
    temp_path = None
    try:
        fd, temp_path = tempfile.mkstemp(suffix='.sqlite')
        with os.fdopen(fd, 'wb') as f:
            f.write(uploaded_file.getvalue())
            
        conn = sqlite3.connect(temp_path)
        
        query = "SELECT name FROM sqlite_master WHERE type='table';"
        tables_df = pd.read_sql_query(query, conn)
        
        if not tables_df.empty:
            for table in tables_df['name'].tolist():
                db_dict[table] = pd.read_sql_query(f"SELECT * FROM {table}", conn)
                
        conn.close()
    except Exception as e:
        print(f"Error loading SQLite database: {e}")
    finally:
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except:
                pass
                
    return db_dict

def get_data_summary(df):
    """Get summary statistics of DataFrame.
    Returns: dict with keys:
      - 'rows': int
      - 'columns': int  
      - 'numeric_columns': list of column names
      - 'categorical_columns': list of column names
      - 'date_columns': list of column names
      - 'missing_values': dict of col -> count of nulls
      - 'memory_usage': str (formatted memory)
      - 'dtypes': dict of col -> dtype string
    """
    if df is None or df.empty:
        return {}
        
    try:
        summary = {
            'rows': len(df),
            'columns': len(df.columns)
        }
        
        summary['numeric_columns'] = df.select_dtypes(include=['number']).columns.tolist()
        summary['date_columns'] = df.select_dtypes(include=['datetime']).columns.tolist()
        summary['categorical_columns'] = df.select_dtypes(include=['object', 'category']).columns.tolist()
        summary['missing_values'] = df.isnull().sum().to_dict()
        
        mem_bytes = df.memory_usage(deep=True).sum()
        if mem_bytes < 1024:
            mem_str = f"{mem_bytes} bytes"
        elif mem_bytes < 1024**2:
            mem_str = f"{mem_bytes/1024:.2f} KB"
        else:
            mem_str = f"{mem_bytes/(1024**2):.2f} MB"
        summary['memory_usage'] = mem_str
        
        summary['dtypes'] = {col: str(dtype) for col, dtype in df.dtypes.items()}
        
        return summary
    except Exception as e:
        print(f"Error generating data summary: {e}")
        return {}
