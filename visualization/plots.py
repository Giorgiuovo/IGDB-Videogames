class chart:
    def __init__(self, 
                 conn,
                 cursor, 
                 x, 
                 y, 
                 fields,
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
        self.fields = fields
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
            "fields": self.fields,
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
    def __init__(self, 
                 conn, 
                 cursor, 
                 x, 
                 y, 
                 fields, 
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
                 trendline=False):
        super().__init__(conn, cursor, x, y, fields, title, x_label, y_label, sort_field, filters, aggregation, group_by, limit, having, offset)
        self.trendline = trendline
    


        
        