from pathlib import Path
import igdb_api_config

if __name__ == "__main__":
    ...

# IGDB
IGDB_CLIENT_ID = igdb_api_config.IGDB_CLIENT_ID
IGDB_CLIENT_SECRET = igdb_api_config.IGDB_CLIENT_SECRET
IGDB_LIMIT = 500  # IGDB-Maximum pro Anfrage

DATA_PATH = Path(__file__).resolve().parent / "data"
DB_MAPPING_PATH =  DATA_PATH / "db_games_map.json"
DB_PATH = DATA_PATH / "games.sqlite"

QUERY_WHITELIST_PATH = DATA_PATH / "db_query_whitelist.json"

PRESET_PATH = DATA_PATH / "presets"