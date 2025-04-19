import os 
import api.fetch_filtered_game_data as data
import db.db_helpers as helpers
import db.schema as schema
import db.insert_data as insert

if __name__ == "__main__":
    while True:
        input_csv = input("soll eine csv Tabelle erstellt werden? (j/n): ")
        if input_csv in ["j", "n"]:
            break
        else:
            print("Ungültige Eingabe, versuche es nochmal")

    while True:
        input_sqlite = input("soll eine SQLite Datenbank erstellt werden? (j/n): ")
        if input_sqlite in ["j", "n"]:
            if not os.path.exists(r"\db\spiele.db"):
                break
            else:
                print("Datenbank schon vorhanden. SQLite-Setup abgebrochen.")
                input_sqlite = "n"
                break
        else:         
            print("Ungültige Eingabe, versuche es nochmal")

    if input_csv == "n" and input_sqlite == "n":
        print("Setup abgebrochen")
    else:
        all_game_data = data.fetch_game_data()
            
        if input_csv == "j":
            pass
        if input_sqlite == "j": 
            conn = helpers.get_connection()
            cursor = conn.cursor()

            # --- SCHEMA ---
            # Mapping-Tabelle erstellen
            schema.create_api2db_map_table(cursor)
            map = [
            # Haupttabelle: games
            {"api_name": "igdb", "api_field_name": "id", "table_name": "games", "table_field_name": "id"},
            {"api_name": "igdb", "api_field_name": "name", "table_name": "games", "table_field_name": "name"},
            {"api_name": "igdb", "api_field_name": "slug", "table_name": "games", "table_field_name": "slug"},
            {"api_name": "igdb", "api_field_name": "summary", "table_name": "games", "table_field_name": "summary"},
            {"api_name": "igdb", "api_field_name": "checksum", "table_name": "games", "table_field_name": "checksum"},
            {"api_name": "igdb", "api_field_name": "url", "table_name": "games", "table_field_name": "url"},
            {"api_name": "igdb", "api_field_name": "first_release_date", "table_name": "games", "table_field_name": "first_release_date"},
            {"api_name": "igdb", "api_field_name": "cover.url", "table_name": "games", "table_field_name": "cover_url"},
            {"api_name": "igdb", "api_field_name": "cover.image_id", "table_name": "games", "table_field_name": "cover_image_id"},
            {"api_name": "igdb", "api_field_name": "aggregated_rating", "table_name": "games", "table_field_name": "aggregated_rating"},
            {"api_name": "igdb", "api_field_name": "aggregated_rating_count", "table_name": "games", "table_field_name": "aggregated_rating_count"},
            {"api_name": "igdb", "api_field_name": "rating", "table_name": "games", "table_field_name": "rating"},
            {"api_name": "igdb", "api_field_name": "rating_count", "table_name": "games", "table_field_name": "rating_count"},
            {"api_name": "igdb", "api_field_name": "total_rating", "table_name": "games", "table_field_name": "total_rating"},

            # Plattformen
            {"api_name": "igdb", "api_field_name": "platforms.id", "table_name": "platforms", "table_field_name": "id"},
            {"api_name": "igdb", "api_field_name": "platforms.name", "table_name": "platforms", "table_field_name": "name"},

            # Genres
            {"api_name": "igdb", "api_field_name": "genres.id", "table_name": "genres", "table_field_name": "id"},
            {"api_name": "igdb", "api_field_name": "genres.name", "table_name": "genres", "table_field_name": "name"},

            # Themes
            {"api_name": "igdb", "api_field_name": "themes.id", "table_name": "themes", "table_field_name": "id"},
            {"api_name": "igdb", "api_field_name": "themes.name", "table_name": "themes", "table_field_name": "name"},

            # Game Modes
            {"api_name": "igdb", "api_field_name": "game_modes.id", "table_name": "game_modes", "table_field_name": "id"},
            {"api_name": "igdb", "api_field_name": "game_modes.name", "table_name": "game_modes", "table_field_name": "name"},

            # Player Perspectives
            {"api_name": "igdb", "api_field_name": "player_perspectives.id", "table_name": "player_perspectives", "table_field_name": "id"},
            {"api_name": "igdb", "api_field_name": "player_perspectives.name", "table_name": "player_perspectives", "table_field_name": "name"},

            # Game Engines
            {"api_name": "igdb", "api_field_name": "game_engines.id", "table_name": "game_engines", "table_field_name": "id"},
            {"api_name": "igdb", "api_field_name": "game_engines.name", "table_name": "game_engines", "table_field_name": "name"},

            # Franchises
            {"api_name": "igdb", "api_field_name": "franchises.id", "table_name": "franchises", "table_field_name": "id"},
            {"api_name": "igdb", "api_field_name": "franchises.name", "table_name": "franchises", "table_field_name": "name"},

            # Collections
            {"api_name": "igdb", "api_field_name": "collections.id", "table_name": "collections", "table_field_name": "id"},
            {"api_name": "igdb", "api_field_name": "collections.name", "table_name": "collections", "table_field_name": "name"}
            ]
            schema.insert_api2db_map(cursor, map)

            # games-Tabelle erstellen
            schema.create_games_table(cursor)

            # Reference- und many to many Tabellen erstellen wenn es gebraucht wird
            mapping = helpers.load_mapping(cursor, "igdb")
            seen_refs = set()
            for _, (table, _) in mapping.items():
                if table != "games" and table not in seen_refs:
                    schema.create_reference_and_m2m_tables(cursor, table)
                    seen_refs.add(table)

            # --- INSERTS ---
            game_inserts, ref_inserts, link_inserts = insert.extract_insert_data(all_game_data, mapping)

            games_data = {
                "games": game_inserts,
                "refs": ref_inserts,
                "links": link_inserts
            }

            insert.insert_game_batches(cursor, games_data)

            helpers.close_connection(conn)
        
        






