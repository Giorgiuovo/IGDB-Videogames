import config
import json
import streamlit as st
import importlib
from streamlit.runtime.caching import cache_resource
from db.db_helpers import get_connection
import db.general_db_search as db_search
import inspect
import uuid
import json

def build_chart_args(plot_type, plot_settings, query_settings, chart_types_config):
    params = {}
    
    chart_config = chart_types_config["plots"].get(plot_type, {})
    if not chart_config:
        return params

    # Get constructor parameters
    ChartClass = get_chart_class(plot_type)
    if not ChartClass:
        return params
        
    constructor_args = inspect.signature(ChartClass.__init__).parameters

    # Handle plot settings
    plot_params = chart_config.get("parameters", {}).get("plot", {})
    for param_name, param_config in plot_params.items():
        if param_name in constructor_args:
            value = plot_settings.get(param_name)
            if value is not None:
                params[param_name] = value


    # Handle query settings
    query_params = chart_config.get("parameters", {}).get("query", {})
    for param_name, param_config in query_params.items():
        if param_name in constructor_args:
            value = query_settings.get(param_name)
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

    presets, reset, save_col, text_input = st.columns([0.15, 0.12, 0.12, 0.61])

    # initialise session state
    if "preset" not in st.session_state:
        st.session_state.preset = "Unsaved preset"

    with reset:
        if st.session_state.preset != "Unsaved preset" and st.button("Delete preset"):
            (config.PRESET_PATH / f"{st.session_state.preset}.json").unlink()
            st.session_state.preset = "Unsaved preset"
            st.rerun()
        elif st.button("Reset plots"):
            empty_json(config.DEFAULT_PRESET_PATH)
            st.rerun()

    with text_input:
        new_preset_name = st.text_input("Save as:", key="new_preset_name")
    with save_col:
        if st.button("Save preset"):
            if new_preset_name:
                unsaved_path = config.DEFAULT_PRESET_PATH
                new_path = config.PRESET_PATH / f"{new_preset_name}.json"
                with open(unsaved_path, "r", encoding="utf-8") as src:
                    data = json.load(src)
                with open(new_path, "w", encoding="utf-8") as dst:
                    json.dump(data, dst, indent=4)
                st.session_state.preset = new_preset_name
                st.success(f"Preset saved as '{new_preset_name}'")
                st.rerun()
            else:
                st.error("Please enter a name to save the preset.")

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
        empty_json(config.DEFAULT_PRESET_PATH)
        st.session_state.preset = "Unsaved preset"
        (config.PRESET_PATH / f"{st.session_state.preset}.json").unlink()
        data = {}
    except FileNotFoundError:
        st.error("Preset file not found. Resetting to default.")
        empty_json(config.DEFAULT_PRESET_PATH)
        st.session_state.preset = "Unsaved preset"
        (config.PRESET_PATH / f"{st.session_state.preset}.json").unlink()
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

        chart_args = build_chart_args(plot_type, plot_settings, query_settings, chart_types_config)

        if "aggregation" not in chart_args:
            chart_args["aggregation"] = query_settings.get("aggregation", {})
        
        chart_instance = ChartClass(
            conn=conn,
            **chart_args
        )

        fig = chart_instance.render(get_data_func=db_search.get_data)
        st.plotly_chart(fig, use_container_width=True, key=f"{uuid.uuid4()}")


    add_page_link, remove_last, rightspace = st.columns([0.15, 0.15, 0.7])
    with add_page_link:
        # add button
        st.page_link("pages/Add Plot.py", label="Add new plot", icon="➕", use_container_width=True)
        
    with remove_last:
        if st.button("Remove last plot"):
            with open((config.PRESET_PATH / f"{st.session_state.preset}.json"), "r") as f:
                data = json.load(f)

            last_key = str(max(map(int, data.keys())))
            del data[last_key]

            with open((config.PRESET_PATH / f"{st.session_state.preset}.json"), "w") as f:
                json.dump(data, f, indent=4)

if __name__ == "__main__":
    show()
