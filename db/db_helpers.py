import sqlite3
from pathlib import Path

def get_connection():
    DB_PATH = Path(__file__).resolve().parent.parent / "data" / "games.db"
    print(DB_PATH)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def load_mapping(cursor, api_name):
    cursor.execute("""
        SELECT api_field_name, table_name, table_field_name
        FROM api2db_map
        WHERE api_name = ?
    """, (api_name,))
    return {field: (table, column) for field, table, column in cursor.fetchall()}

def close_connection(conn):
    conn.commit()
    conn.close()