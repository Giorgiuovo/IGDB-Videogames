import sqlite3
import json
import config

def get_connection(row = True):
    conn = sqlite3.connect(config.DB_PATH)
    if row:
        conn.row_factory = sqlite3.Row
    return conn

def load_mapping(api_name = "igdb"):
    with open(config.DB_MAPPING_PATH, "r", encoding="utf-8") as f:
        mapping_list = json.load(f)

    return {
        entry["api_field_name"]: (entry["table_name"], entry["table_field_name"])
        for entry in mapping_list
        if entry["api_name"] == api_name
    }

def close_connection(conn):
    conn.commit()
    conn.close()