import sqlite3
import json
import config

def get_connection(row = True):
    conn = sqlite3.connect(config.DB_PATH, check_same_thread=False)
    if row:
        conn.row_factory = sqlite3.Row
    return conn

def generate_whitelist_from_mapping(mapping_path, output_path):
    with open(mapping_path, encoding="utf-8") as f:
        mapping = json.load(f)
    
    whitelist = {}

    def field_type_to_ops(field_type):
        if field_type == "text":
            return "str", ["=", "LIKE", "IN"]
        if field_type == "integer":
            return "int", ["=", ">", "<", ">=", "<=", "BETWEEN"]
        if field_type == "float":
            return "float", ["=", ">", "<", ">=", "<=", "BETWEEN"]
        if field_type == "datetime":
            return "datetime", ["=", ">", "<", ">=", "<=", "BETWEEN"]
        raise ValueError(f"Unknown type {field_type}")

    for table, table_data in mapping["tables"].items():
        for field, data in table_data.get("fields", {}).items():
            api_field = data["api_field"]
            field_type, ops = field_type_to_ops(data["type"])
            whitelist[api_field if "." in api_field else f"{table}.{field}"] = {
                "type": field_type,
                "operators": ops
            }
        for rel_name, rel_data in table_data.get("relations", {}).items():
            whitelist[f"{rel_data['api_field']}.name"] = {
                "type": "str",
                "operators": ["=", "LIKE", "IN"]
            }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(whitelist, f, indent=2)

def load_mapping(mapping_path):
    with open(mapping_path, encoding="utf-8") as f:
        mapping_json = json.load(f)
    
    mapping_list = []

    for table_name, table_data in mapping_json["tables"].items():
        # Fields
        for field_name, field_data in table_data.get("fields", {}).items():
            api_field = field_data["api_field"]
            mapping_list.append((api_field, table_name, field_name))

        # Relations (nur ID & Name!)
        if "relations" in table_data:
            for rel_name, rel_data in table_data["relations"].items():
                target_table = rel_data["target_table"]
                mapping_list.append((f"{rel_data['api_field']}.id", target_table, "id"))
                mapping_list.append((f"{rel_data['api_field']}.name", target_table, "name"))

    return mapping_list

def close_connection(conn):
    conn.commit()
    conn.close()