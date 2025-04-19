print(f":::))) Fertig! {len(game_data)} Spiele gespeichert in der SQLite-Datenbank 'spiele.db'")
for game in game_data:
    cursor.execute("""
    INSERT OR REPLACE INTO games (
        id, name, slug, summary, url, first_release_date,
        aggregated_rating, aggregated_rating_count,
        rating, rating_count, total_rating
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        game.get("id"),
        game.get("name"),
        game.get("slug"),
        game.get("summary"),
        game.get("url"),
        game.get("first_release_date"),
        game.get("aggregated_rating"),
        game.get("aggregated_rating_count"),
        game.get("rating"),
        game.get("rating_count"),
        game.get("total_rating")
    ))