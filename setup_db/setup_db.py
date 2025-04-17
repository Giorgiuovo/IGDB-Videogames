import os # #### !!!!!!!!!!!!!! pathlib
import api.fetch_filtered_game_data as filtered_data
import db.schema as schema

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
    all_game_data = filtered_data.fetch_game_data()
    if input_csv == "j":
        pass
    if input_sqlite == "j": 
        schema.create_db()

# filename = "hallohallo.json"
# with open(filename, "w", encoding="utf-8") as f:
#     json.dump(all_game_data, f, indent=4, ensure_ascii=False)
