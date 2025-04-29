import config
import plotly.express as px
import plotly.graph_objects as go
import json
import pandas as pd
import numpy as np
from statsmodels.nonparametric.smoothers_lowess import lowess
from typing import Optional, Dict, List, Union

class Chart:
    def __init__(self, 
                 conn, 
                 title: str = "",
                 sort_fields: Optional[List[Dict]] = None,
                 filters: Optional[List[Dict]] = None, 
                 aggregation: Optional[Dict] = None,
                 group_by: Optional[List[str]] = None,
                 limit: Optional[int] = None,
                 having: Optional[List[Dict]] = None,
                 offset: Optional[int] = None
                 ):
        self.conn = conn
        self.title = title
        self.sort_fields = sort_fields or []
        self.filters = filters or []
        self.aggregation = aggregation or {}
        self.group_by = group_by or []
        self.limit = limit
        self.having = having or []
        self.offset = offset
    
    def get_query_args(self) -> Dict:
        """Prepare query arguments for db_search.get_data"""
        return {
            "conn": self.conn,
            "fields": list(getattr(self, "fields", set())),
            "sort_fields": self.sort_fields,
            "filters": self.filters,
            "aggregation": self.aggregation,
            "group_by": self.group_by,
            "limit": self.limit,
            "having": self.having,
            "offset": self.offset
        }
    
    def get_dataframe(self, get_data) -> pd.DataFrame:
        """Execute query and return processed DataFrame"""
        args = self.get_query_args()
        df = get_data(**args)

        with open(config.QUERY_WHITELIST_PATH, "r", encoding="utf-8") as f:
            whitelist = json.load(f)

        # Handle datetime conversion
        for col in df.columns:
            whitelist_key = col
            if whitelist_key not in whitelist and f"games.{col}" in whitelist:
                whitelist_key = f"games.{col}"

            if whitelist_key in whitelist and whitelist[whitelist_key]["type"] == "datetime":
                df[col] = pd.to_datetime(df[col], unit='s')

        return df
    
    def render(self, get_data_func) -> go.Figure:
        """Render the chart (to be implemented by subclasses)"""
        raise NotImplementedError("Subclasses must implement render()")


class LineChart(Chart):
    def __init__(
        self, 
        conn,
        x: str, 
        y: str, 
        title: str = "", 
        x_label: Optional[str] = None, 
        y_label: Optional[str] = None,
        sort_fields: Optional[List[Dict]] = None, 
        filters: Optional[List[Dict]] = None, 
        aggregation: Optional[Dict] = None, 
        group_by: Optional[List[str]] = None, 
        limit: Optional[int] = None, 
        having: Optional[List[Dict]] = None, 
        offset: Optional[int] = None,
        trendline: bool = False,
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
        # Handle aggregated fields (prefixed with "agg:")
        self.x = x.replace("games.", "").replace("agg:", "")
        self.y = y.replace("games.", "").replace("agg:", "")
        
        # Store original x/y for field selection
        self.original_x = x
        self.original_y = y
        
        # Fields should include the actual database fields, not aggregation aliases
        self.fields = set()
        if x.startswith("agg:"):
            self.fields.add(x.replace("agg:", ""))
        else:
            self.fields.add(x)
        if y.startswith("agg:"):
            self.fields.add(y.replace("agg:", ""))
        else:
            self.fields.add(y)
            
        self.x_label = x_label
        self.y_label = y_label
        self.trendline = trendline

    def render(self, get_data_func) -> go.Figure:
        df = self.get_dataframe(get_data_func)
        
        # Use the original field names for plotting
        x_col = self.original_x.replace("games.", "").replace("agg:", "")
        y_col = self.original_y.replace("games.", "").replace("agg:", "")
        
        if x_col in df.columns:
            df = df.sort_values(by=x_col)

        fig = px.line(
            df,
            x=x_col,
            y=y_col,
            title=self.title,
            labels={
                x_col: self.x_label or x_col,
                y_col: self.y_label or y_col
            }
        )

        if self.trendline:
            df[y_col] = pd.to_numeric(df[y_col], errors="coerce")
            df = df.dropna(subset=[x_col, y_col])

            x_values = df[x_col]
            y_values = df[y_col]

            if np.issubdtype(x_values.dtype, np.datetime64):
                x_numeric = pd.to_datetime(x_values).astype(int) / 10**9
            else:
                x_numeric = x_values.values

            smoothed = lowess(y_values, x_numeric, frac=0.1)
            fig.add_trace(go.Scatter(
                x=pd.to_datetime(smoothed[:, 0], unit="s") if isinstance(x_values.iloc[0], pd.Timestamp) else smoothed[:, 0],
                y=smoothed[:, 1],
                mode='lines',
                name='Smoothed Trend',
                line=dict(color='red', dash='dash')
            ))

            slope, intercept = np.polyfit(x_numeric, y_values, 1)
            fig.add_trace(go.Scatter(
                x=x_values,
                y=intercept + slope * x_numeric,
                mode='lines',
                name='Linear Trend',
                line=dict(color='green', dash='dot')
            ))

        return fig


class BarChart(Chart):
    def __init__(
        self, 
        conn, 
        x: str, 
        y: str, 
        title: str = "", 
        x_label: Optional[str] = None, 
        y_label: Optional[str] = None,
        orientation: bool = False,
        sort_fields: Optional[List[Dict]] = None, 
        filters: Optional[List[Dict]] = None, 
        aggregation: Optional[Dict] = None, 
        group_by: Optional[List[str]] = None, 
        limit: Optional[int] = None, 
        having: Optional[List[Dict]] = None, 
        offset: Optional[int] = None
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
        # Store the original references exactly as provided
        self.x = x
        self.y = y
        self.x_label = x_label
        self.y_label = y_label
        self.orientation = orientation

        # Fields should include the actual database fields needed for the query
        self.fields = set()
        if not x.startswith("agg:"):
            self.fields.add(x)
        if not y.startswith("agg:"):
            self.fields.add(y)

    def render(self, get_data_func) -> go.Figure:
        df = self.get_dataframe(get_data_func)
        
        # Get the exact column names from the dataframe
        x_col = self.x.replace("agg:", "") if self.x.startswith("agg:") else self.x
        y_col = self.y.replace("agg:", "") if self.y.startswith("agg:") else self.y
        
        # Verify columns exist in dataframe
        if x_col not in df.columns:
            raise ValueError(f"Column '{x_col}' not found in dataframe. Available columns: {list(df.columns)}")
        if y_col not in df.columns:
            raise ValueError(f"Column '{y_col}' not found in dataframe. Available columns: {list(df.columns)}")
        
        fig = px.bar(
            df,
            x=y_col if self.orientation else x_col,
            y=x_col if self.orientation else y_col,
            title=self.title,
            orientation='h' if self.orientation else 'v',
            labels={
                x_col: self.x_label or x_col,
                y_col: self.y_label or y_col
            }
        )
        return fig

class PieChart(Chart):
    def __init__(
        self,
        conn,
        labels: str,
        values: str,
        title: str = "",
        sort_fields: Optional[List[Dict]] = None,
        filters: Optional[List[Dict]] = None,
        aggregation: Optional[Dict] = None,
        group_by: Optional[List[str]] = None,
        limit: Optional[int] = None,
        having: Optional[List[Dict]] = None,
        offset: Optional[int] = None
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
        self.labels = labels
        self.values = values

        self.fields = set()
        if not labels.startswith("agg:"):
            self.fields.add(labels)
        if not values.startswith("agg:"):
            self.fields.add(values)

    def render(self, get_data_func) -> go.Figure:
        df = self.get_dataframe(get_data_func)

        label_col = self.labels.replace("agg:", "") if self.labels.startswith("agg:") else self.labels
        value_col = self.values.replace("agg:", "") if self.values.startswith("agg:") else self.values

        if label_col not in df.columns:
            raise ValueError(f"Label column '{label_col}' not found in dataframe. Available columns: {list(df.columns)}")
        if value_col not in df.columns:
            raise ValueError(f"Value column '{value_col}' not found in dataframe. Available columns: {list(df.columns)}")

        fig = px.pie(
            df,
            names=label_col,
            values=value_col,
            title=self.title
        )
        return fig

class ScatterPlot(Chart):
    def __init__(
        self,
        conn,
        x: str,
        y: str,
        title: str = "",
        x_label: Optional[str] = None,
        y_label: Optional[str] = None,
        sort_fields: Optional[List[Dict]] = None,
        filters: Optional[List[Dict]] = None,
        aggregation: Optional[Dict] = None,
        group_by: Optional[List[str]] = None,
        limit: Optional[int] = None,
        having: Optional[List[Dict]] = None,
        offset: Optional[int] = None
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
        self.x = x
        self.y = y
        self.x_label = x_label
        self.y_label = y_label

        self.fields = set()
        if not x.startswith("agg:"):
            self.fields.add(x)
        if not y.startswith("agg:"):
            self.fields.add(y)

    def render(self, get_data_func) -> go.Figure:
        df = self.get_dataframe(get_data_func)

        x_col = self.x.replace("agg:", "") if self.x.startswith("agg:") else self.x
        y_col = self.y.replace("agg:", "") if self.y.startswith("agg:") else self.y

        if x_col not in df.columns:
            raise ValueError(f"Column '{x_col}' not found in dataframe. Available columns: {list(df.columns)}")
        if y_col not in df.columns:
            raise ValueError(f"Column '{y_col}' not found in dataframe. Available columns: {list(df.columns)}")

        fig = px.scatter(
            df,
            x=x_col,
            y=y_col,
            title=self.title,
            labels={
                x_col: self.x_label or x_col,
                y_col: self.y_label or y_col
            }
        )
        return fig


        
        