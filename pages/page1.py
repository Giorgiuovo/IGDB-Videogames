from config import PRESET_PATH as preset_path
import pathlib
import streamlit as st

def right_aligned_columns(num_fields, field_width=0.15):
    """
    Erstellt rechtsbündige Spalten für `num_fields` Felder,
    jedes Feld mit `field_width` Breite.
    Der restliche Platz bleibt links als leerer Spacer.
    """
    total_field_width = num_fields * field_width
    if total_field_width >= 1:
        raise ValueError("Zu viele Felder oder Feldbreite zu groß für 100% Breite.")
    
    spacer_width = 1 - total_field_width
    layout = [spacer_width] + [field_width] * num_fields
    return st.columns(layout)

def show():
    st.set_page_config(layout = "wide")

    presets, middle_space, search = st.columns([0.15, 0.7, 0.15])

    with presets:
        st.selectbox("select Preset", ["Unsaved preset"] if not any(preset_path.iterdir()) else ["Unsaved Preset"] + [f.stem for f in preset_path.iterdir() if f.is_file()])

    with search:
        st.text_input("search")

    if "plus" not in st.session_state:
        st.session_state.plus = False

    if st.session_state.plus:
        new_chart = st.selectbox("Plot type", ["","linechart"])
        if new_chart == "linechart":
            st.text("basic")
            cols_basic = right_aligned_columns(3)
            cols_basic[1].selectbox("title")
            cols_basic[2].selectbox("x_label")
            cols_basic[3].selectbox("y_label")
            cols_data = right_aligned_columns()
            x, y, extra_fields, sort_field, filters, aggregation, group_by, limit, having, offset, trendline = st.columns ()
        st.session_state.chart(False)   

    if st.button("➕ Add new plot"):
        st.session_state.plus = True
    


if __name__ == "__main__":
    show()
