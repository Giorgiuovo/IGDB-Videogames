import config
import api.api_helpers as helpers
import requests
from pathlib import Path
import csv
import time

def load_id_set(filename):
    with open(filename, newline="", encoding="utf-8") as f:
        return {int(row[0]) for row in csv.reader(f) if row and row[0].isdigit()}

def format_id_list(id_set):
    return ",".join(map(str, id_set))

def fetch_game_data():
    offset = 0

    DATA_PATH = Path(__file__).resolve().parent.parent / "data"
    blocked_keywords = load_id_set(Path(DATA_PATH) / "filtered_igdb_keywords.csv")
    print(f"{len(blocked_keywords)} blockierte Keywords geladen.")
    allowed_platforms = load_id_set(Path(DATA_PATH) / "filtered_igdb_platforms.csv")
    print(f"{len(allowed_platforms)} erlaubte Plattformen geladen.")

    blocked_str = format_id_list(blocked_keywords)
    allowed_str = format_id_list(allowed_platforms)
    
    all_game_data = []

    while True:
        query = f'''
        fields id, name, slug, summary, checksum, url, platforms.name, genres.name, themes.name, game_modes.name,
                player_perspectives.name, game_engines.name, franchises.name, collections.name, keywords.name, language_supports.language.name, first_release_date,
                cover.url, cover.image_id, aggregated_rating, aggregated_rating_count, rating, rating_count, total_rating;
        where platforms = ({allowed_str}) 
                & ((keywords = null) | (keywords != ({blocked_str})))
                & ((rating_count > 5) | (aggregated_rating_count > 0))
                & game_type = (0,4,6,8,9,11);
        sort id asc;
        limit {config.IGDB_LIMIT};
        offset {offset};
        '''
        response = requests.post("https://api.igdb.com/v4/games", headers=helpers.HEADERS, data=query)

        if response.status_code != 200:
            print(f"Fehler: {response.status_code}, Offset: {offset}")
            break

        data = response.json()
        if not data:
            print("Keine weiteren Spiele gefunden.")
            break
        
        all_game_data.extend(data)
        print(f"Offset {offset}: insgesamt {len(all_game_data)} Spiele")
        offset += config.IGDB_LIMIT

        time.sleep(0.25)

    return all_game_data

