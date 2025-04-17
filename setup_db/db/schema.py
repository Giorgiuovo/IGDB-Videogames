import sqlite3

def get_connection():
    conn = sqlite3.connect("spiele.db")
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def create_many_to_many(cursor, table_name):
    table_name = table_name.lower()
    cursor.execute(f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        id INTEGER PRIMARY KEY,
        name TEXT
    )
    """)

    cursor.execute(f"""
    CREATE TABLE IF NOT EXISTS games_{table_name} (
        game_id INTEGER,
        {table_name}_id INTEGER,
        PRIMARY KEY (game_id, {table_name}_id),
        FOREIGN KEY (game_id) REFERENCES games(id),
        FOREIGN KEY ({table_name}_id) REFERENCES {table_name}(id)
    )
    """)

def create_db():
    with get_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS games (
            id INTEGER PRIMARY KEY,
            name TEXT,
            slug TEXT,
            summary TEXT,
            checksum TEXT,
            url TEXT,
            first_release_date INTEGER,
            cover_url TEXT,
            cover_image_id INTEGER,
            aggregated_rating REAL,
            aggregated_rating_count INTEGER,
            rating REAL,
            rating_count INTEGER,
            total_rating REAL
        )
        """)

        mtm_columns = ["platforms", "genres", "themes", "keywords", "game_modes", 
                    "player_perspectives", "game_engines", "franchises", "collections", "languages"]
        for column in mtm_columns:
            create_many_to_many(column)

        conn.commit()
        conn.close()
    
