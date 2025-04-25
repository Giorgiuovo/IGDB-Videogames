
def extract_insert_data(games_data, mapping):
    game_inserts = []
    ref_inserts = {}
    link_inserts = {}
    
    def find_id_name_recursive(data):
        """goes recursively through data until (id, name) pairs are found"""
        results = []

        if isinstance(data, dict):
            if "id" in data and "name" in data:
                results.append((data["id"], data["name"]))
            else:
                for value in data.values():
                    results.extend(find_id_name_recursive(value))

        elif isinstance(data, list):
            for item in data:
                results.extend(find_id_name_recursive(item))

        return results

    for game_data in games_data:
        game_entry = {"id": game_data["id"]}

        for api_field, table, column in mapping:
            data = game_data
            parts = api_field.split(".")
            for part in parts:
                if isinstance(data, dict) and part in data:
                    data = data[part]
                elif isinstance(data, list):
                    break
                else:
                    data = None
                    break

            if data is None:
                continue

            if table == "games":
                game_entry[column] = data

            else:
                found_entries = find_id_name_recursive(data)
                for sub_id, sub_name in found_entries:
                    ref_inserts.setdefault(table, set()).add((sub_id, sub_name))
                    link_table = f"games_{table}"
                    link_inserts.setdefault(link_table, set()).add((game_data["id"], sub_id))

        game_inserts.append(game_entry)

    return game_inserts, ref_inserts, link_inserts



def insert_game_batches(cursor, games_data):
    print("Spiele:", len(games_data.get("games", [])))
    print("Referenzen:", {k: len(v) for k, v in games_data.get("refs", {}).items()})
    print("Links:", {k: len(v) for k, v in games_data.get("links", {}).items()})
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