import db.db_helpers as helpers
import json
import builtins
import config

def validate_get_data_input(fields: list, sort_field, filters: list):
    if not fields:
        raise ValueError("Field is missing")
    
    if fields == ["*"] and len(fields) > 1:
        raise ValueError("Cannot select * and another field")
    
    with open(config.QUERY_WHITELIST_PATH, "r", encoding="utf-8") as f:
        whitelist = json.load(f)
        allowed_fields = set(whitelist)

        if sort_field not in allowed_fields:
            raise ValueError(f"Sort-field '{sort_field}' not allowed")

        for field in fields:
            if field not in allowed_fields:
                raise ValueError(f"Field '{field}' not allowed")

        if filters:
            for f in filters:
                field = f["field"]
                op = f["op"]
                value = f["value"]

                if field not in allowed_fields:
                    raise ValueError(f"Filter field '{field}' not allowed")

                allowed_ops = whitelist[field]["operators"]
                type_name = whitelist[field]["type"]

                if op not in allowed_ops:
                    raise ValueError(f"Operator '{op}' not allowed for '{field}'")

                try:
                    expected_type = getattr(builtins, type_name)
                except AttributeError:
                    raise ValueError(f"Unsupported type '{type_name}' in whitelist")

                if op in ("BETWEEN", "IN"):
                    if not isinstance(value, (list, tuple)):
                        raise ValueError(f"Operator '{op}' requires a list or tuple")
                    if not all(isinstance(v, expected_type) for v in value):
                        raise ValueError(f"All values for '{field}' must be of type '{type_name}'")
                else:
                    if not isinstance(value, expected_type):
                        raise ValueError(f"Value for '{field}' must be of type '{type_name}'")


def get_data(cursor, fields: list, sort_field: str = None, asc_dsc: bool = True, filters: list = None, df: bool = False):
    if sort_field is None and fields:
        sort_field = fields[0]
    filters = filters or []
    validate_get_data_input(fields, sort_field, filters)

    mapping = helpers.load_mapping()
    field_table_map = {}
    for e in mapping:
        field_table_map[e[0]] = e[1]
        field_table_map["languages.name"] = "languages"
        if e[1] == "games":
            field_table_map[f"{e[1]}.{e[2]}"] = e[1]

    if fields == ["*"]:
        join_fields = {field_table for field_table in field_table_map.values()} - {"games"}
        select_lines = ["*"]
        query_parts = []
    else:
        filter_fields = [f["field"] for f in filters]
        combined_fields = set(fields).union(filter_fields)
        join_fields = {field for field in combined_fields if field_table_map.get(field) != "games"}
        select_lines = [field for field in fields if field_table_map.get(field) == "games"]
        query_parts = [f"{field} IS NOT NULL" for field in fields]

    join_lines = []
    for join in join_fields:
        join = join.replace(".name", "")
        join_lines.append(
            f"LEFT JOIN games_{join} ON games.id = games_{join}.game_id\n"
            f"LEFT JOIN {join} ON games_{join}.{join}_id = {join}.id"
        )
        select_lines.append(f"GROUP_CONCAT(DISTINCT {join}.name) as {join}")
    
    sort_line = f"{sort_field} {"" if asc_dsc == True else "DSC"}"

    params = []
    for f in filters:
        field = f["field"]
        op = f["op"]
        val = f["value"]

        if op == "BETWEEN":
            query_parts.append(f"{field} BETWEEN ? AND ?")
            params.extend(val)
        elif op == "IN":
            placeholders = ", ".join(["?"] * len(val))
            query_parts.append(f"{field} IN ({placeholders})")
            params.extend(val)
        else:
            query_parts.append(f"{field} {op} ?")
            params.append(val)

    query = f"""
    SELECT {",\n".join(select_lines)}
    FROM games
    {"\n".join(join_lines)}
    {"WHERE " + " AND ".join(query_parts) if query_parts else ""}
    GROUP BY games.id
    ORDER BY {sort_line}
    """

    if not df:
        try:
            cursor.execute(query, params)
        except Exception as e:
            print("Failed Query:\n", query)
            print("With Params:\n", params)
            raise e

        return [dict(row) for row in cursor.fetchall()]
    else:
        return query, params

