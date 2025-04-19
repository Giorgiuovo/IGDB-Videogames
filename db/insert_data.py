def extract_insert_data(games_data, mapping):
    game_inserts = []
    ref_inserts = {}
    link_inserts = {}

    for game_data in games_data:
        game_entry = {"id": game_data["id"]}  # Immer id für INSERT

        for field, (table, column) in mapping.items():
            data = game_data
            parts = field.split(".")
            for part in parts:
                if isinstance(data, dict) and part in data:
                    data = data[part]
                else:
                    data = None
                    break

            if data is None:
                continue

            if table == "games":
                game_entry[column] = data

            elif isinstance(data, list):
                for entry in data:
                    if isinstance(entry, int):
                        sub_id = entry
                        sub_name = None
                    elif isinstance(entry, dict):
                        sub_id = entry.get("id")
                        sub_name = entry.get("name")
                    else:
                        continue

                    ref_inserts.setdefault(table, set()).add((sub_id, sub_name))
                    link_table = f"games_{table}"
                    link_inserts.setdefault(link_table, set()).add((game_data["id"], sub_id))

        game_inserts.append(game_entry)

    return game_inserts, ref_inserts, link_inserts


def insert_game_batches(cursor, games_data):
    # Spiele einfügen
    if games_data["games"]:
        columns = sorted({key for game in games_data["games"] for key in game})
        placeholders = ", ".join(["?"] * len(columns))
        column_str = ", ".join(columns)
        values = [tuple(game.get(col) for col in columns) for game in games_data["games"]]
        cursor.executemany(
            f"INSERT OR IGNORE INTO games ({column_str}) VALUES ({placeholders})",
            values
        )

    # Referenztabellen einfügen
    for table, values in games_data["refs"].items():
        cursor.executemany(
            f"INSERT OR IGNORE INTO {table} (id, name) VALUES (?, ?)",
            values
        )

    # Linktabellen einfügen
    for link_table, values in games_data["links"].items():
        ref_name = link_table.split("_", 1)[1]
        cursor.executemany(
            f"INSERT OR IGNORE INTO {link_table} (game_id, {ref_name}_id) VALUES (?, ?)",
            values
        )