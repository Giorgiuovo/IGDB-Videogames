import db.db_helpers as helpers

def get_data(cursor, fields: list, filters: tuple, operators: tuple, filter_values: tuple):
    query_parts = []
    params = []

    for i in range(len(filters)):
        query_parts.append(f"{filters[i]} {operators[i]} ?")
        params.append(filter_values[i])

    query = f"""
    SELECT {", ".join(fields)}
    FROM games
    {"WHERE " + " AND ".join(query_parts) if query_parts else ""}
    """
    
    cursor.execute(query, params)
    return [dict(row) for row in cursor.fetchall()]
    









def get_filtered_data_all(cursor, main_data: str, filter_data: tuple[str, str, str], sort_data: str):
    # mapping = helpers.load_mapping()
    
    # filtered_refs = set()
    # for field, (table, column) in mapping.items():
    #     if table != "games":
    #         filtered_refs.add(table)
    
    cursor.execute(f"""
        SELECT ?, ?, ?
        FROM games
        WHERE ? ? ?
        
    """, main_data, filter_data[0], sort_data, filter_data[0], filter_data[1], filter_data[2])

    return [dict(row) for row in cursor.fetchall()]
    



def get_data_one_game(cursor, name):
    mapping = helpers.load_mapping()
    
    seen_refs = set()
    for _, (table, _) in mapping.items():
        if table != "games":
            seen_refs.add(table)

    join_lines = []
    select_lines = ["games.*"]
    for ref in seen_refs:
        join_lines.append(
            f"LEFT JOIN games_{ref} ON games.id = games_{ref}.game_id\n"
            f"LEFT JOIN {ref} ON games_{ref}.{ref}_id = {ref}.id"
        )
        select_lines.append(f"GROUP_CONCAT(DISTINCT {ref}.name) as {ref}")
    prepared_joins = "\n".join(join_lines)
    prepared_selects = "\n".join(select_lines)
    # print(prepared_joins)
    cursor.execute(f"""
        SELECT * 
        FROM games
        {prepared_joins}
        WHERE games.slug = ?
        GROUP BY games.id
    """, (name,))
    return [dict(row) for row in cursor.fetchall()]
