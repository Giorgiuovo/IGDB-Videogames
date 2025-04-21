from config import DB_PATH
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
        if input_sqlite in ["j", "n", "debug_trotzdem"]:
            if input_sqlite in ["j", "debug_trotzdem"] and not DB_PATH.exists():
                break
            elif input_sqlite == "debug_trotzdem":
                DB_PATH.unlink()
                break
            elif input_sqlite == "n":
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

        if input_sqlite in ["j", "debug_trotzdem"]: 
            conn = helpers.get_connection(False)
            cursor = conn.cursor()

            # --- INSERTS ---
            # games-Tabelle erstellen
            schema.create_games_table(cursor)

            # Reference- und many-to-many-Tabellen erstellen, wenn gebraucht
            mapping = helpers.load_mapping() 
            seen_refs = set()

            for _, table, _ in mapping:
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