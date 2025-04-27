import config
import json
import pathlib
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
    st.set_page_config(layout="wide")
    st.write("## Preset Overview")

    presets, middle_space, search = st.columns([0.15, 0.7, 0.15])

    if "preset" not in st.session_state:
        st.session_state.preset = None

    with presets:
        st.session_state.preset = st.selectbox(
            "Select preset", [f.stem for f in config.PRESET_PATH.iterdir() if f.is_file()]
        )
        if st.session_state.preset != "Unsaved Preset":
            if st.button("Delete preset"):
                empty_json(config.PRESET_PATH / "Unsaved Preset.json")
                st.session_state.preset = "Unsaved Preset"
        else:
            if st.button("Reset plots"):
                empty_json(config.PRESET_PATH / "Unsaved Preset.json")

    with search:
        st.text_input("search")

    add_page_link, rightspace = st.columns([0.2, 0.8])
    with add_page_link:
        st.page_link("pages/Add Plot.py", label="Add new plot", icon="➕", use_container_width=True)

    # Load the selected preset
    with open(f"{config.PRESET_PATH}/{st.session_state.preset}.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        st.session_state.pos = len(list(data.keys()))

    # Dummy data for demonstration (replace with your SQL results!)
    dummy_df = pd.DataFrame({
        "games.url": ["url1", "url2", "url3"],
        "games.first_release_date": [2020, 2021, 2022],
        "games.name": ["Game A", "Game B", "Game C"],
        "games.slug": [10, 20, 30],
        "cover.url": ["cover1", "cover2", "cover3"],
        "games.aggregated_rating": [75, 82, 90]
    })

    # Render each plot in the preset
    for key, plot_config in data.items():
        st.markdown(f"### Plot {key}")
        fig = render_plot_from_config(plot_config, dummy_df)
        st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    show()
