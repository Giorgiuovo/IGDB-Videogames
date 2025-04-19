import db.db_helpers as helpers


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
