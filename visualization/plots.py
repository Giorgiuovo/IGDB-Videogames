import plotly.express as px
import plotly.graph_objects as go
import json
import pandas as pd

class chart:
    def __init__(self, 
                 conn, 
                 title="",
                 sort_fields=None,
                 filters=None, 
                 aggregation=None,
                 group_by = None,
                 limit = None,
                 having=None,
                 offset=None
                 ):
        self.conn = conn
        self.title = title
        self.sort_fields = sort_fields
        self.filters = filters
        self.aggregation = aggregation
        self.group_by = group_by
        self.limit = limit
        self.having = having
        self.offset = offset
    
    def get_query_args(self):
        return {
            "conn": self.conn,
            "fields": getattr(self, "fields", None),
            "sort_fields": self.sort_fields,
            "filters": self.filters,
            "aggregation": self.aggregation,
            "group_by": self.group_by,
            "limit": self.limit,
            "having": self.having,
            "offset": self.offset
            }
    
    def get_dataframe(self, get_data):
        args = self.get_query_args()
        df = get_data(**args)

        from config import QUERY_WHITELIST_PATH
        with open(QUERY_WHITELIST_PATH, "r", encoding="utf-8") as f:
            whitelist = json.load(f)

        # Versuche beide Varianten: mit und ohne "games."
        for col in df.columns:
            whitelist_key = col
            if whitelist_key not in whitelist and f"games.{col}" in whitelist:
                whitelist_key = f"games.{col}"

            if whitelist_key in whitelist and whitelist[whitelist_key]["type"] == "datetime":
                df[col] = pd.to_datetime(df[col], unit='s')

        return df
    
    def render(self, get_data_func):
        raise NotImplementedError("subclasses have to implement render()")


class line_chart(chart):
    def __init__(
        self, 
        conn,
        x, 
        y, 
        title="", 
        x_label=None, 
        y_label=None, 
        sort_fields=None, 
        filters=None, 
        aggregation=None, 
        group_by=None, 
        limit=None, 
        having=None, 
        offset=None,
        trendline=False
    ):
        super().__init__(
            conn=conn,
            title=title,
            sort_fields=sort_fields,
            filters=filters,
            aggregation=aggregation,
            group_by=group_by,
            limit=limit,
            having=having,
            offset=offset
        )
        self.x = x.replace("games.", "")
        self.y = y.replace("games.", "")
        self.fields = {x} | {y}
        self.x_label = x_label
        self.y_label = y_label
        self.trendline = trendline

    def render(self, get_data_func):
        df = self.get_dataframe(get_data_func)
        if self.x in df.columns:
            df = df.sort_values(by=self.x, ascending=True)

        fig = px.line(
            df,
            x=self.x,
            y=self.y,
            title=self.title,
            labels={
                self.x: self.x_label if self.x_label else self.x,
                self.y: self.y_label if self.y_label else self.y
            }
            
        )

        if self.trendline:
            fig.add_trace(go.Scatter(
                x=df[self.x],
                y=df[self.y],
                mode='lines',
                name='Trendline'
            ))

        return fig
    


        
        