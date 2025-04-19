import db.basic_db_functions as functions
import db.db_helpers as helpers

conn = helpers.get_connection()
cursor = conn.cursor()
test = functions.get_data_one_game(cursor, "quake")
print(test)


# def main():
#     while True:
#         to_csv_or_sqlite = input("sollen die Spielenamen und Slugs in eine csv gespeichert werden oder soll eine sqlite Datenbank erstellt werden?\nwenn csv: csv     wenn sqlite: sqlite\n")

#         if to_csv_or_sqlite in ("csv", "sqlite"):
#             break
#         else:
#             print("Ungültige Eingabe. Versuche es nochmal.\nwenn csv: csv     wenn sqlite: sqlite")

#     blocked_keywords = load_id_set("filtered_igdb_keywords.csv")
#     print(f"{len(blocked_keywords)} blockierte Keywords geladen.")

#     allowed_platforms = load_id_set("filtered_igdb_platforms.csv")
#     print(f"{len(allowed_platforms)} erlaubte Plattformen geladen.")

#     all_game_data = fetch_game_data(blocked_keywords, allowed_platforms)

#     # filename = "hallohallo.json"
#     # with open(filename, "w", encoding="utf-8") as f:
#     #     json.dump(all_game_data, f, indent=4, ensure_ascii=False)
#     if to_csv_or_sqlite == "csv":
#         save_games_to_csv(all_game_data)
#     elif to_csv_or_sqlite == "sqlite":
#         save_games_to_sqlite(all_game_data)

# if __name__ == "__main__":
#   main()