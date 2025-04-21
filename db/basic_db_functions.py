import db.db_helpers as helpers
import json
import builtins
import config

def validate_get_data_input(fields: list, filters: list, operators: list, filter_values: list):
    if not (len(filters) == len(operators) == len(filter_values)):
        raise ValueError("Unequal amount of filters, operators or filter_values")

    if fields == []:
        raise ValueError("Field is missing")
    
    if fields == ["*"] and len(fields) > 1:
        raise ValueError("Cannot select * and another field")
    
    with open(config.QUERY_WHITELIST_PATH, "r", encoding="utf-8") as f:
        whitelist = json.load(f)
        allowed_fields = set(whitelist)

        for field in fields:
            if field not in allowed_fields:
                raise ValueError(f"Field '{field}' not allowed")

        for i, filter_field in enumerate(filters):
            if filter_field not in allowed_fields:
                raise ValueError(f"Filter field '{filter_field}' not allowed")

            allowed_ops = whitelist[filter_field]["operators"]
            type_name = whitelist[filter_field]["type"]

            if operators[i] not in allowed_ops:
                raise ValueError(f"Operator '{operators[i]}' not allowed for '{filter_field}'")

            try:
                expected_type = getattr(builtins, type_name)
            except AttributeError:
                raise ValueError(f"Unsupported type '{type_name}' in whitelist")

            if operators[i] in ("BETWEEN", "IN"):
                if not isinstance(filter_values[i], (list, tuple)):
                    raise ValueError(f"Operator '{operators[i]}' requires a list or tuple")
                if not all(isinstance(v, expected_type) for v in filter_values[i]):
                    raise ValueError(f"All values for '{filter_field}' must be of type '{type_name}'")
            else:
                if not isinstance(filter_values[i], expected_type):
                    raise ValueError(f"Value for '{filter_field}' must be of type '{type_name}'")
                

def get_data(cursor, fields: list, filters: list, operators: list, filter_values: list):
    validate_get_data_input(fields, filters, operators, filter_values)

    mapping = helpers.load_mapping()
    field_table_map = {}
    for e in mapping:
        field_table_map[e[2]] = e[1]
    
    if fields == ["*"]:
        join_fields = {field_table for field_table in field_table_map.values()} - {"games"}
        select_lines = ["*"]
    else:
        fields_filters = set(fields).union(set(filters))
        join_fields = {field for field in fields_filters if field_table_map[field] != "games"}
        select_lines = [f"{", ".join(field for field in fields)}"]
    
    join_lines = []
    for join in join_fields:
        join_lines.append(
            f"LEFT JOIN games_{join} ON games.id = games_{join}.game_id\n"
            f"LEFT JOIN {join} ON games_{join}.{join}_id = {join}.id"
        )
        select_lines.append(f"GROUP_CONCAT(DISTINCT {join}.name) as {join}")

    query_parts = []
    params = []
    prepared_joins = "\n".join(join_lines)
    prepared_selects = ",\n".join(select_lines)
    for i in range(len(filters)):
        if operators[i] == "BETWEEN":
            query_parts.append(f"{filters[i]} BETWEEN ? AND ?")
            params.extend(filter_values[i])
        elif operators[i] == "IN":
            placeholders = ", ".join(["?"] * len(filter_values[i]))
            query_parts.append(f"{filters[i]} IN ({placeholders})")
            params.extend(filter_values[i])
        else:
            query_parts.append(f"{filters[i]} {operators[i]} ?")
            params.append(filter_values[i])

    query = f"""
    SELECT {prepared_selects}
    FROM games
    {prepared_joins}
    {"WHERE " + " AND ".join(query_parts) if query_parts else ""}
    GROUP BY games.id
    """
    
    try:
        cursor.execute(query, params)
    except Exception as e:
        print("Failed Query:\n", query)
        print("With Params:\n", params)
        raise e

    return [dict(row) for row in cursor.fetchall()]
    



def get_data_one_game(cursor, name):
    mapping = helpers.load_mapping()

    # Alle referenzierten Tabellen sammeln (außer "games")
    seen_refs = {table for _, table, _ in mapping if table != "games"}

    join_lines = []
    select_lines = ["games.*"]
    for ref in seen_refs:
        join_lines.append(
            f"LEFT JOIN games_{ref} ON games.id = games_{ref}.game_id\n"
            f"LEFT JOIN {ref} ON games_{ref}.{ref}_id = {ref}.id"
        )
        select_lines.append(f"GROUP_CONCAT(DISTINCT {ref}.name) as {ref}")

    prepared_joins = "\n".join(join_lines)
    prepared_selects = ",\n".join(select_lines)

    cursor.execute(f"""
        SELECT {prepared_selects}
        FROM games
        {prepared_joins}
        WHERE games.slug = ?
        GROUP BY games.id
    """, (name,))

    return [dict(row) for row in cursor.fetchall()]

