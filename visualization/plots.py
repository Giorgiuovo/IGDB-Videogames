import plotly.express as px
import plotly.graph_objects as go

class chart:
    def __init__(self, 
                 conn,
                 cursor, 
                 x, 
                 y, 
                 extra_fields=None,
                 title="", 
                 x_label=None, 
                 y_label=None, 
                 sort_field=None,
                 filters=None, 
                 aggregation=None,
                 group_by = None,
                 limit = None,
                 having=None,
                 offset=None
                 ):
        self.conn = conn
        self.cursor = cursor
        self.x = x
        self.y = y
        self.fields = extra_fields
        self.title = title
        self.x_label = x_label
        self.y_label = y_label
        self.sort_field = sort_field
        self.filters = filters
        self.aggregation = aggregation
        self.group_by = group_by
        self.limit = limit
        self.having = having
        self.offset = offset
    
    def get_query_args(self):
        return {
            "conn": self.conn,
            "fields": self.extra_fields,
            "sort_field": self.sort_field,
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
        return df
    
    def render(self, get_data_func):
        raise NotImplementedError("Subklassen müssen render() implementieren.")


class line_chart(chart):
    def __init__(
        self, 
        conn, 
        cursor, 
        x, 
        y, 
        extra_fields=None, 
        title="", 
        x_label=None, 
        y_label=None, 
        sort_field=None, 
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
            cursor=cursor,
            x=x,
            y=y,
            extra_fields=extra_fields,
            title=title,
            x_label=x_label,
            y_label=y_label,
            sort_field=sort_field,
            filters=filters,
            aggregation=aggregation,
            group_by=group_by,
            limit=limit,
            having=having,
            offset=offset
        )
        self.trendline = trendline

    def render(self, get_data_func):
        df = self.get_dataframe(get_data_func)

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
    


        
        