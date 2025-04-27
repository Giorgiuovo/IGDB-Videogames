import config
import json
from pathlib import Path
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

def empty_json(path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump({}, f)

def render_plot_from_config(plot_config, data_source):
    plot_type = plot_config.get("plot_type")
    plot_settings = plot_config.get("plot_settings", {})

    if plot_type == "line_chart":
        fig = px.line(
            data_source,
            x=plot_settings.get("x"),
            y=plot_settings.get("y"),
            title=plot_settings.get("title", None),
            labels={
                plot_settings.get("x"): plot_settings.get("x_label", ""),
                plot_settings.get("y"): plot_settings.get("y_label", "")
            }
        )
        if plot_settings.get("trendline"):
            fig.add_trace(go.Scatter(
                x=data_source[plot_settings.get("x")],
                y=data_source[plot_settings.get("y")],
                mode='lines',
                name='Trendline'
            ))
        return fig
    else:
        return go.Figure().add_annotation(text="Plot type not supported")

def show():
    # Stelle sicher, dass das Verzeichnis existiert
    config.PRESET_PATH.mkdir(parents=True, exist_ok=True)
    
    # Erstelle eine gültige leere JSON-Datei, falls nicht vorhanden
    default_preset_path = config.PRESET_PATH / "Unsaved preset.json"
    if not default_preset_path.exists():
        empty_json(default_preset_path)

    st.set_page_config(layout="wide")
    st.write("## Preset Overview")

    presets, middle_space, search = st.columns([0.15, 0.7, 0.15])

    # Initialisiere den Session-State
    if "preset" not in st.session_state:
        st.session_state.preset = "Unsaved preset"

    with presets:
        # Liste der verfügbaren Presets (nur .json-Dateien)
        preset_files = [f.stem for f in config.PRESET_PATH.glob("*.json") if f.is_file()]
        if not preset_files:  # Falls keine Presets existieren
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
        empty_json(config.PRESET_PATH / f"{st.session_state.preset}.json")
        data = {}
    except FileNotFoundError:
        st.error("Preset file not found. Resetting to default.")
        empty_json(config.PRESET_PATH / f"{st.session_state.preset}.json")
        data = {}

    st.session_state.pos = len(list(data.keys()))

    # HIER PLOTS
    
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
                empty_json(default_preset_path)
                st.rerun()

if __name__ == "__main__":
    show()
