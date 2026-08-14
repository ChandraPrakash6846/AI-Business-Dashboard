import pandas as pd
from sqlalchemy import create_engine, inspect

def create_db_engine(db_type, host=None, port=None, database=None, username=None, password=None, sqlite_path=None):
    """
    Creates an SQLAlchemy database engine for SQLite, MySQL, or PostgreSQL.
    """
    if db_type == "SQLite":
        if not sqlite_path:
            raise ValueError("SQLite database file path is required.")
        import os
        abs_path = os.path.abspath(sqlite_path).replace('\\', '/')
        if os.path.isdir(abs_path):
            raise ValueError(f"The path '{sqlite_path}' is a folder directory, not a .db database file. Please specify a database file (e.g. C:/path/to/database.db).")
        os.makedirs(os.path.dirname(abs_path), exist_ok=True)
        connection_string = f"sqlite:///{abs_path}"


    elif db_type == "PostgreSQL":
        connection_string = f"postgresql://{username}:{password}@{host}:{port}/{database}"
    elif db_type == "MySQL":
        connection_string = f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}"
    else:
        raise ValueError(f"Unsupported DB type: {db_type}")

    engine = create_engine(connection_string)
    return engine

def list_tables(engine):
    """
    Returns list of tables available in the database.
    """
    inspector = inspect(engine)
    return inspector.get_table_names()

def load_table_data(engine, table_name, limit=5000):
    """
    Loads data from a specified table.
    """
    query = f"SELECT * FROM {table_name} LIMIT {limit}"
    return pd.read_sql_query(query, engine)

def seed_sample_sql_database(sqlite_path):
    """
    Populates sample business SQL tables (sales_orders, product_catalog, customer_directory)
    in the SQLite database so the SQL feature works 100% instantly on any system out of the box.
    """
    import os
    abs_path = os.path.abspath(sqlite_path).replace('\\', '/')
    os.makedirs(os.path.dirname(abs_path), exist_ok=True)
    engine = create_engine(f"sqlite:///{abs_path}")
    
    # Check if sample tables exist
    tables = list_tables(engine)
    if "sales_orders" not in tables:
        # Create sample tables
        df_sales = pd.DataFrame([
            {"order_id": "ORD-2001", "customer_name": "Acme Corp", "category": "Technology", "sales": 4500.0, "profit": 950.0, "region": "North"},
            {"order_id": "ORD-2002", "customer_name": "Global Tech", "category": "Furniture", "sales": 2300.0, "profit": 350.0, "region": "East"},
            {"order_id": "ORD-2003", "customer_name": "Nexus Ltd", "category": "Office Supplies", "sales": 890.0, "profit": 210.0, "region": "South"},
            {"order_id": "ORD-2004", "customer_name": "Starlight Co", "category": "Technology", "sales": 6700.0, "profit": 1400.0, "region": "West"},
            {"order_id": "ORD-2005", "customer_name": "Apex Group", "category": "Furniture", "sales": 1250.0, "profit": 180.0, "region": "North"}
        ])
        df_sales.to_sql("sales_orders", engine, if_exists="replace", index=False)

    if "product_catalog" not in tables:
        df_products = pd.DataFrame([
            {"product_id": "PROD-101", "product_name": "Enterprise Laptop", "category": "Technology", "unit_price": 1200.0, "stock": 45},
            {"product_id": "PROD-102", "product_name": "Ergonomic Desk Chair", "category": "Furniture", "unit_price": 350.0, "stock": 80},
            {"product_id": "PROD-103", "product_name": "Wireless Headset", "category": "Technology", "unit_price": 150.0, "stock": 120},
            {"product_id": "PROD-104", "product_name": "Standing Desk", "category": "Furniture", "unit_price": 650.0, "stock": 30}
        ])
        df_products.to_sql("product_catalog", engine, if_exists="replace", index=False)

    return engine


def execute_sql_dump_script(sql_content_str, sqlite_path):
    """
    Executes a raw SQL script file (.sql dump) into SQLite, converting MySQL/PostgreSQL dialect if necessary.
    """
    import os, re, sqlite3
    abs_path = os.path.abspath(sqlite_path).replace('\\', '/')
    os.makedirs(os.path.dirname(abs_path), exist_ok=True)
    
    # Preprocess SQL script to strip MySQL-specific statements incompatible with SQLite
    cleaned_sql = sql_content_str
    cleaned_sql = re.sub(r'ENGINE\s*=\s*\w+', '', cleaned_sql, flags=re.IGNORECASE)
    cleaned_sql = re.sub(r'DEFAULT\s+CHARSET\s*=\s*\w+', '', cleaned_sql, flags=re.IGNORECASE)
    cleaned_sql = re.sub(r'AUTO_INCREMENT\s*=\s*\d+', '', cleaned_sql, flags=re.IGNORECASE)
    cleaned_sql = re.sub(r'LOCK\s+TABLES\s+[^;]+;', '', cleaned_sql, flags=re.IGNORECASE)
    cleaned_sql = re.sub(r'UNLOCK\s+TABLES\s*;', '', cleaned_sql, flags=re.IGNORECASE)
    cleaned_sql = re.sub(r'/\*![\s\S]*?\*/;', '', cleaned_sql)

    conn = sqlite3.connect(abs_path)
    cursor = conn.cursor()
    
    try:
        cursor.executescript(cleaned_sql)
        conn.commit()
    except Exception as e:
        # Fallback: execute statements line by line, skipping unsupported statements
        statements = cleaned_sql.split(';')
        for stmt in statements:
            stmt_clean = stmt.strip()
            if stmt_clean:
                try:
                    cursor.execute(stmt_clean)
                except Exception:
                    pass
        conn.commit()
    finally:
        conn.close()

    engine = create_engine(f"sqlite:///{abs_path}")
    return engine


