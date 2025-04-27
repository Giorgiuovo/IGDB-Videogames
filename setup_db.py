import config
import api.fetch_filtered_game_data as data
import db.db_helpers as helpers
import db.schema as schema
import db.insert_data as insert

if __name__ == "__main__":
    while True:
        input_csv = input("do you want to generate a .csv export? (y/n): ")
        if input_csv in ["y", "n"]:
            break
        else:
            print("Invalid Input, try again")

    while True:
        input_sqlite = input("should an SQLite database be created? (y/n): ")
        if input_sqlite in ["y", "n", "debug_trotzdem"]:
            if input_sqlite in ["y", "debug_trotzdem"] and not config.DB_PATH.exists():
                break
            elif input_sqlite == "debug_trotzdem":
                config.DB_PATH.unlink()
                break
            elif input_sqlite == "n":
                break
            else:
                print("Database already exists. SQLite setup canceled.")
                input_sqlite = "n"
                break
        else:         
            print("Invalid Input, try again")

    if input_csv == "n" and input_sqlite == "n":
        print("Setup canceled")
    else:
        all_game_data = data.fetch_game_data()
            
        if input_csv == "y":
            pass

        if input_sqlite in ["y", "debug_trotzdem"]: 
            conn = helpers.get_connection(False)
            cursor = conn.cursor()

            # --- SCHEMA ---
            # create games-table
            schema.create_games_table(cursor)

            # Create reference and many-to-many tables, if required
            mapping = helpers.load_mapping(config.DB_MAPPING_PATH) 
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

            #config.QUERY_WHITELIST_PATH.unlink()
            #helpers.generate_whitelist_from_mapping(config.DB_MAPPING_PATH, config.QUERY_WHITELIST_PATH)
            config.PRESET_PATH.mkdir(exist_ok=True)


            print("Setup finished")
            helpers.close_connection(conn)