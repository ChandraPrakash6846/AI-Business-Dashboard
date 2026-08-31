# AI Business Dashboard - Fully Updated & Verified
import pandas as pd
import numpy as np

def load_dataset(file_or_path):
    """
    Load dataset from file buffer, path, or existing DataFrame. Supports CSV, Excel (.xlsx, .xls), SQL scripts (.sql), and SQLite DB (.db, .sqlite).
    """
    if isinstance(file_or_path, pd.DataFrame):
        return file_or_path

    filename = file_or_path.lower() if isinstance(file_or_path, str) else getattr(file_or_path, 'name', '').lower()


    if filename.endswith('.csv'):
        return pd.read_csv(file_or_path)
    elif filename.endswith(('.xlsx', '.xls')):
        return pd.read_excel(file_or_path)
    elif filename.endswith('.sql'):
        from modules.sql_connector import execute_sql_dump_script, list_tables, load_table_data
        if hasattr(file_or_path, 'getvalue'):
            sql_text = file_or_path.getvalue().decode('utf-8', errors='ignore')
        elif hasattr(file_or_path, 'read'):
            sql_text = file_or_path.read().decode('utf-8', errors='ignore')
        else:
            with open(file_or_path, 'r', encoding='utf-8', errors='ignore') as f:
                sql_text = f.read()
        import os
        temp_path = os.path.abspath("temp_sql_import.db").replace('\\', '/')
        engine = execute_sql_dump_script(sql_text, temp_path)
        tables = list_tables(engine)
        if not tables:
            raise ValueError("No SQL tables found in .sql script file.")
        if len(tables) == 1:
            return load_table_data(engine, tables[0])
        else:
            tbl_dfs = [load_table_data(engine, t) for t in tables]
            return merge_multiple_datasets(tbl_dfs, mode="join")
    elif filename.endswith(('.db', '.sqlite', '.sqlite3')):
        from modules.sql_connector import create_db_engine, list_tables, load_table_data
        import os
        if not isinstance(file_or_path, str):
            temp_path = os.path.abspath(f"temp_db_{getattr(file_or_path, 'name', 'upload.db')}").replace('\\', '/')
            with open(temp_path, "wb") as f_out:
                f_out.write(file_or_path.getbuffer())
            path = temp_path
        else:
            path = file_or_path
        engine = create_db_engine("SQLite", sqlite_path=path)
        tables = list_tables(engine)
        if not tables:
            raise ValueError("No tables found in SQLite database file.")
        if len(tables) == 1:
            return load_table_data(engine, tables[0])
        else:
            tbl_dfs = [load_table_data(engine, t) for t in tables]
            return merge_multiple_datasets(tbl_dfs, mode="join")
    else:
        # Fallback attempt
        try:
            return pd.read_csv(file_or_path)
        except Exception:
            if hasattr(file_or_path, 'seek'):
                file_or_path.seek(0)
            return pd.read_excel(file_or_path)


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
            
            # Attempt numeric conversion (stripping $, commas, %, 'free', and extracting numbers)
            clean_str = cleaned_df[col].astype(str).str.lower().str.replace('free', '0', regex=False).str.replace('not available', '0', regex=False).str.replace('$', '', regex=False).str.replace(',', '', regex=False).str.replace('%', '', regex=False).str.strip()
            numeric_converted = pd.to_numeric(clean_str, errors='coerce')
            if numeric_converted.notnull().sum() > 0.3 * len(cleaned_df):
                cleaned_df[col] = numeric_converted
            else:
                extracted = clean_str.str.extract(r'(\d+(?:\.\d+)?)')[0]
                num_extracted = pd.to_numeric(extracted, errors='coerce')
                if num_extracted.notnull().sum() > 0.3 * len(cleaned_df):
                    cleaned_df[col] = num_extracted

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
    # Auto-create derived sales & profit if quantityOrdered & priceEach are present
    cols = df.columns
    cols_lower = [c.lower() for c in cols]
    
    if "sales" not in cols_lower and "revenue" not in cols_lower:
        if "quantityordered" in cols_lower and "priceeach" in cols_lower:
            q_col = cols[cols_lower.index("quantityordered")]
            p_col = cols[cols_lower.index("priceeach")]
            df['Sales'] = pd.to_numeric(df[q_col], errors='coerce') * pd.to_numeric(df[p_col], errors='coerce')
            cols = df.columns
            cols_lower = [c.lower() for c in cols]

    if "profit" not in cols_lower:
        if "sales" in cols_lower and "buyprice" in cols_lower and "quantityordered" in cols_lower:
            s_col = cols[cols_lower.index("sales")]
            b_col = cols[cols_lower.index("buyprice")]
            q_col = cols[cols_lower.index("quantityordered")]
            df['Profit'] = pd.to_numeric(df[s_col], errors='coerce') - (pd.to_numeric(df[b_col], errors='coerce') * pd.to_numeric(df[q_col], errors='coerce'))
            cols = df.columns
            cols_lower = [c.lower() for c in cols]

    def match(keywords):
        for kw in keywords:
            for i, c in enumerate(cols_lower):
                if kw in c:
                    return cols[i]
        return None

    mapping = {
        "sales": match(['sales', 'revenue', 'turnover', 'amount', 'total_amount', 'rental_rate', 'priceeach', 'price', 'rate', 'cost']),
        "profit": match(['profit', 'margin', 'gain', 'net_income', 'earnings', 'amount']),
        "quantity": match(['qty', 'quantity', 'quantityordered', 'count', 'units']),
        "date": match(['date', 'time', 'orderdate', 'rental_date', 'payment_date', 'last_update', 'day', 'timestamp']),
        "category": match(['category', 'productline', 'type', 'group', 'product_type', 'department', 'rating', 'title']),
        "region": match(['region', 'country', 'state', 'city', 'location', 'zone', 'district']),
        "customer": match(['customername', 'customer_name', 'customer_id', 'first_name', 'last_name', 'customer', 'client', 'user', 'buyer'])
    }
    return mapping

def merge_multiple_datasets(file_list, mode="auto", join_key=None):
    """
    Merges or concatenates multiple uploaded files (CSV/Excel) into a unified DataFrame.
    - mode="auto": Automatically detects whether files are relational tables or sales period files.
    - mode="concat": Vertically stacks files (e.g. Sales_Jan.csv, Sales_Feb.csv)
    - mode="join": Horizontally joins files on common primary/foreign key columns
    """
    if not file_list:
        raise ValueError("No files provided for merging.")

    file_tuples = []
    for idx, f in enumerate(file_list):
        if isinstance(f, pd.DataFrame):
            fname = f"df_table_{idx}"
            df_temp = f
        else:
            fname = getattr(f, 'name', str(f)).lower()
            df_temp = load_dataset(f)
        file_tuples.append((fname, df_temp))


    if len(file_tuples) == 1:
        return file_tuples[0][1]

    # Auto-detect relational database tables (e.g., orders, orderdetails, customers, employees, offices)
    relational_keywords = ['order', 'customer', 'employee', 'office', 'product', 'detail', 'payment']
    is_relational = any(any(kw in fname for fname, _ in file_tuples) for kw in relational_keywords)

    if mode == "auto":
        mode = "join" if is_relational else "concat"

    if mode == "join":
        # Relational Smart Join Strategy
        # Sort files so fact tables come first
        sorted_files = sorted(file_tuples, key=lambda item: 0 if any(k in item[0] for k in ['detail', 'line', 'item', 'order', 'fact', 'sale']) else 1)
        
        merged_df = sorted_files[0][1].copy()
        
        for fname, next_df in sorted_files[1:]:
            # Find common join columns
            common_keys = [c for c in next_df.columns if c in merged_df.columns]
            if common_keys:
                key = common_keys[0]
                # Drop overlapping non-key columns to prevent collision
                overlap = [c for c in next_df.columns if c in merged_df.columns and c != key]
                next_clean = next_df.drop(columns=overlap)
                merged_df = pd.merge(merged_df, next_clean, on=key, how="left")
            else:
                # Check foreign key mapping (e.g., salesRepEmployeeNumber -> employeeNumber)
                fk_mapped = False
                if "salesrepemployeenumber" in [c.lower() for c in merged_df.columns] and "employeenumber" in [c.lower() for c in next_df.columns]:
                    fk1 = [c for c in merged_df.columns if c.lower() == "salesrepemployeenumber"][0]
                    fk2 = [c for c in next_df.columns if c.lower() == "employeenumber"][0]
                    overlap = [c for c in next_df.columns if c in merged_df.columns and c != fk2]
                    next_clean = next_df.drop(columns=overlap)
                    merged_df = pd.merge(merged_df, next_clean, left_on=fk1, right_on=fk2, how="left")
                    fk_mapped = True

                if not fk_mapped:
                    # Fallback to concat if no common key
                    merged_df = pd.concat([merged_df, next_df], ignore_index=True)

        return merged_df

    else:
        # Concatenate / Stack Rows
        return pd.concat([df for _, df in file_tuples], ignore_index=True)
