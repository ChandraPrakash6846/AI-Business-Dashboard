import sqlite3
import pandas as pd
from datetime import datetime
import os

class AnalysisHistory:
    """SQLite-backed analysis history tracker."""
    
    def __init__(self, db_path=None):
        """Initialize with a database path."""
        if db_path is None:
            # Default to project directory
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            db_path = os.path.join(base_dir, 'history.db')
            
        self.db_path = db_path
        
        # Ensure directory exists
        db_dir = os.path.dirname(self.db_path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)
        
        self._init_db()
        
    def _init_db(self):
        """Create table if it doesn't exist."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT,
                        filename TEXT,
                        action TEXT,
                        details TEXT,
                        result_summary TEXT
                    )
                ''')
                conn.commit()
        except Exception as e:
            print(f"Database initialization error: {e}")
            
    def log_action(self, filename, action, details='', result_summary=''):
        """Log an analysis action."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                timestamp = datetime.now().isoformat()
                cursor.execute('''
                    INSERT INTO history (timestamp, filename, action, details, result_summary)
                    VALUES (?, ?, ?, ?, ?)
                ''', (timestamp, filename, action, details, result_summary))
                conn.commit()
        except Exception as e:
            print(f"Error logging action: {e}")
            
    def get_history(self):
        """Get all history entries ordered by timestamp DESC."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                query = "SELECT * FROM history ORDER BY timestamp DESC"
                df = pd.read_sql_query(query, conn)
                return df
        except Exception as e:
            print(f"Error retrieving history: {e}")
            return pd.DataFrame(columns=['id', 'timestamp', 'filename', 'action', 'details', 'result_summary'])
            
    def clear_history(self):
        """Delete all history entries."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM history')
                conn.commit()
        except Exception as e:
            print(f"Error clearing history: {e}")
            
    def get_recent(self, n=10):
        """Get the n most recent entries."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                query = f"SELECT * FROM history ORDER BY timestamp DESC LIMIT {n}"
                df = pd.read_sql_query(query, conn)
                return df
        except Exception as e:
            print(f"Error retrieving recent history: {e}")
            return pd.DataFrame(columns=['id', 'timestamp', 'filename', 'action', 'details', 'result_summary'])
