import config
import json
from pathlib import Path
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import importlib
import pandas as pd
import visualization.plots as plots
from streamlit.runtime.caching import cache_resource
from db.db_helpers import get_connection
import db.general_db_search as db_search
import inspect
import uuid
import json

def build_chart_args(plot_type, plot_settings, query_settings, chart_types_config):
    params = {}

    # Alle möglichen Parameter für diesen Chart aus chart_types.json
    chart_config = chart_types_config["plots"].get(plot_type)
    if not chart_config:
        return params

    # Constructor-Argumente der Plot-Klasse holen:
    constructor_args = inspect.signature(get_chart_class(plot_type).__init__).parameters

    # Die Parameter aus chart_types.json ("plot" und "query") abgleichen:
    for section in ["plot", "query"]:
        section_params = chart_config.get("parameters", {}).get(section, {})
        for param_name in section_params:
            if param_name in constructor_args:
                # Zuerst plot_settings, dann query_settings durchsuchen:
                value = plot_settings.get(param_name) if section == "plot" else query_settings.get(param_name)
                if value is not None:
                    params[param_name] = value

    return params

def empty_json(path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump({}, f)

def get_chart_class(plot_type):
    # Dynamisch die entsprechende Chart-Klasse laden
    try:
        chart_module = importlib.import_module("visualization.plots")
        chart_class = getattr(chart_module, plot_type)
        return chart_class
    except (ImportError, AttributeError):
        st.error(f"Chart type '{plot_type}' not supported")
        return None
    

def show():
    st.set_page_config(layout="wide")
    st.write("## Preset Overview")
    
    @st.cache_resource
    def get_db_connection():
        return get_connection()

    conn = get_db_connection()

    presets, middle_space, search = st.columns([0.15, 0.7, 0.15])

    # initialise session state
    if "preset" not in st.session_state:
        st.session_state.preset = "Unsaved preset"

    with presets:
        # List of available presets
        preset_files = [f.stem for f in config.PRESET_PATH.glob("*.json") if f.is_file()]
        if not preset_files:  
            preset_files = ["Unsaved preset"]

        st.session_state.preset = st.selectbox(
            "Select preset",
            preset_files,
            index=preset_files.index(st.session_state.preset) if st.session_state.preset in preset_files else 0
        )

    # load presets
    try:
        with open(config.PRESET_PATH / f"{st.session_state.preset}.json", "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError:
        st.error("Invalid JSON in preset file. Resetting to default.")
        empty_json(config.PRESET_PATH / f"{config.DEFAULT_PRESET_PATH}.json")
        st.session_state.preset = "Unsaved preset"
        data = {}
    except FileNotFoundError:
        st.error("Preset file not found. Resetting to default.")
        empty_json(config.PRESET_PATH / f"{config.DEFAULT_PRESET_PATH}.json")
        st.session_state.preset = "Unsaved preset"
        data = {}

    st.session_state.pos = len(list(data.keys()))

    # PLOTS
    with open(config.CHART_TYPES_PATH, "r", encoding="utf-8") as f:
        chart_types_config = json.load(f)

    for key, plot_config in data.items():
        plot_type = plot_config.get("plot_type")
        plot_settings = plot_config.get("plot_settings", {})
        query_settings = plot_config.get("query_settings", {})

        ChartClass = get_chart_class(plot_type)
        if ChartClass is None:
            continue

        # Build constructor args dynamisch:
        chart_args = build_chart_args(plot_type, plot_settings, query_settings, chart_types_config)
        
        # Zusätzliche Pflicht-Args (conn, cursor) ergänzen:
        chart_instance = ChartClass(
            conn=conn,
            **chart_args
        )

        fig = chart_instance.render(get_data_func=db_search.get_data)
        st.plotly_chart(fig, use_container_width=True, key=f"{uuid.uuid4()}")


    add_page_link, rightspace = st.columns([0.2, 0.8])
    with add_page_link:
        # add button
        st.page_link("pages/Add Plot.py", label="Add new plot", icon="➕", use_container_width=True)
        # reset button
        if st.session_state.preset != "Unsaved preset":
                if st.button("Delete preset"):
                    (config.PRESET_PATH / f"{st.session_state.preset}.json").unlink()
                    st.session_state.preset = "Unsaved preset"
                    st.rerun()
        else:
            if st.button("Reset plots"):
                empty_json(config.DEFAULT_PRESET_PATH)
                st.rerun()

if __name__ == "__main__":
    show()
