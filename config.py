from pathlib import Path
import igdb_api_config

if __name__ == "__main__":
    ...

# IGDB
IGDB_CLIENT_ID = igdb_api_config.IGDB_CLIENT_ID
IGDB_CLIENT_SECRET = igdb_api_config.IGDB_CLIENT_SECRET
IGDB_LIMIT = 500  # IGDB-Maximum pro Anfrage

DB_MAPPING_PATH = Path(__file__).resolve().parent / "data" / "games_map.json"
DB_PATH = Path(__file__).resolve().parent / "data" / "games.sqlite"