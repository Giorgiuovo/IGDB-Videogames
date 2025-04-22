import db.general_db_search as functions
import db.db_helpers as helpers
from datetime import datetime
import csv
import config
from pathlib import Path
import pandas as pd

conn = helpers.get_connection()
cursor = conn.cursor()
def load_name_set(filename):
    with open(filename, newline="", encoding="utf-8") as f:
        return {str(row[1]) for row in csv.reader(f) if row and isinstance(row[1], str)
}
platform_names = load_name_set(config.data_path / "filtered_igdb_platforms.csv")
df = functions.get_data(conn,
                                   cursor, 
                                   fields=["platforms.name"], 
                                   filters=[{"field": "platforms.name", "op": "IN", "value": list(platform_names)},
                                            {"field": "first_release_date", "op": ">", "value": datetime(2020, 1, 1)}],  
                                   df = True, 
                                   group_by=["platforms.name"],  
                                   aggregation={"average_user_rating": {"field": "rating", "function": "AVG"},
                                                "average_critic_rating": {"field": "aggregated_rating", "function": "AVG"},
                                                "Spieleanzahl": {"field": "games.name", "function": "COUNT"}})


print(df)
# if __name__ == "__main__":
#     main()
