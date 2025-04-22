from config import PRESET_PATH as preset_path
import pathlib
import streamlit as st

def show():
    st.set_page_config(layout = "wide")

    presets, middle_space, search = st.columns([0.15, 0.7, 0.15])

    with presets:
        st.selectbox("select Preset", ["Unsaved preset"] if not any(preset_path.iterdir()) else ["Unsaved Preset"] + [f.stem for f in preset_path.iterdir() if f.is_file()])

    with search:
        st.text_input("search")

    if "charts" not in st.session_state:
        st.session_state.charts = []

    if st.button("➕ Add new plot"):
        st.session_state.charts.append(True)
    
    
# if "plots" not in st.session_state:
#     st.session_state.plots = []

# if st.selectbox


# st.title("Videogames")

if __name__ == "__main__":
    show()
