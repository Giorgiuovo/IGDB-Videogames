def create_api2db_map_table(cursor):
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS api2db_map (
        api_name TEXT,
        api_field_name TEXT,
        table_name TEXT NOT NULL,
        table_field_name TEXT NOT NULL,
        PRIMARY KEY (api_name, api_field_name)
    )
    """)

def insert_api2db_map(cursor, mapping_list):
    for entry in mapping_list:
        cursor.execute("""
            INSERT OR IGNORE INTO api2db_map (
                api_name, api_field_name, table_name, table_field_name
            ) VALUES (?, ?, ?, ?)
        """, (
            entry["api_name"],
            entry["api_field_name"],
            entry["table_name"],
            entry["table_field_name"]
        ))

def create_games_table(cursor):
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


def create_reference_and_m2m_tables(cursor, table):
    cursor.execute(f"""
    CREATE TABLE IF NOT EXISTS {table} (
        id INTEGER PRIMARY KEY,
        name TEXT
    )
    """)

    cursor.execute(f"""
    CREATE TABLE IF NOT EXISTS games_{table} (
        game_id INTEGER,
        {table}_id INTEGER,
        PRIMARY KEY (game_id, {table}_id),
        FOREIGN KEY (game_id) REFERENCES games(id),
        FOREIGN KEY ({table}_id) REFERENCES {table}(id)
    )
    """)