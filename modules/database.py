import sqlite3
import json
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "dashboard_history.db")

def init_db():
    """Initialize the SQLite database for analysis history."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT,
            timestamp TEXT,
            row_count INTEGER,
            col_count INTEGER,
            summary_json TEXT,
            insights_json TEXT,
            kpis_json TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS nl_queries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            query TEXT,
            result_summary TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_analysis_history(filename, row_count, col_count, summary, insights, kpis):
    """Save an analysis session to history."""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
        INSERT INTO history (filename, timestamp, row_count, col_count, summary_json, insights_json, kpis_json)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        filename,
        timestamp,
        row_count,
        col_count,
        json.dumps(summary, default=str),
        json.dumps(insights, default=str),
        json.dumps(kpis, default=str)
    ))
    conn.commit()
    conn.close()

def save_nl_query(query, result_summary):
    """Save natural language query to history."""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
        INSERT INTO nl_queries (timestamp, query, result_summary)
        VALUES (?, ?, ?)
    """, (timestamp, query, result_summary))
    conn.commit()
    conn.close()

def fetch_history(limit=10):
    """Retrieve recent analysis history."""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, filename, timestamp, row_count, col_count, summary_json, insights_json, kpis_json
        FROM history ORDER BY id DESC LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    conn.close()
    
    result = []
    for r in rows:
        result.append({
            "id": r[0],
            "filename": r[1],
            "timestamp": r[2],
            "row_count": r[3],
            "col_count": r[4],
            "summary": json.loads(r[5]) if r[5] else {},
            "insights": json.loads(r[6]) if r[6] else [],
            "kpis": json.loads(r[7]) if r[7] else {}
        })
    return result

def fetch_query_history(limit=15):
    """Retrieve recent NL queries."""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, timestamp, query, result_summary FROM nl_queries ORDER BY id DESC LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [{"id": r[0], "timestamp": r[1], "query": r[2], "result": r[3]} for r in rows]

def clear_history():
    """Clear all analysis history."""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM history")
    cursor.execute("DELETE FROM nl_queries")
    conn.commit()
    conn.close()
