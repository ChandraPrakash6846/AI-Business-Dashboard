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

def execute_sql_query(engine, query):
    """
    Executes a custom SQL query and returns results dataframe.
    """
    return pd.read_sql_query(query, engine)
