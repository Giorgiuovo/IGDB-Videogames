from config import PRESET_PATH as preset_path
import pathlib
import streamlit as st  

def show():
    st.set_page_config(layout = "wide")
    st.write("This is a sample")
    presets, middle_space, search = st.columns([0.15, 0.7, 0.15])

    with presets:
        st.selectbox("select Preset", ["Unsaved preset"] if not any(preset_path.iterdir()) else ["Unsaved Preset"] + [f.stem for f in preset_path.iterdir() if f.is_file()])

    with search:
        st.text_input("search")
    
    add_page_link, rightspace = st.columns([0.2, 0.8])
    with add_page_link:
        st.page_link("pages/Add Plot.py", label = "Add new plot", icon = "➕", use_container_width=True)

    


if __name__ == "__main__":
    show()
# if __name__ == "__main__":
#     main()
