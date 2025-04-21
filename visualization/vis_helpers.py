import pandas as pd
import db.basic_db_functions as functions

def get_data_in_df(conn, query, params):
    df = pd.read_sql_query(query, conn, params=params)
    return df