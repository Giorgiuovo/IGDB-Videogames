import streamlit as st


def right_aligned_columns(num_fields, field_width=0.15):

    total_field_width = num_fields * field_width
    if total_field_width >= 1:
        raise ValueError("Zu viele Felder oder Feldbreite zu groß für 100% Breite.")
    
    spacer_width = 1 - total_field_width
    layout = [spacer_width] + [field_width] * num_fields
    return st.columns(layout)

def new_chart():
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
    
def show():
    select_plot, middlespace, abort = st.columns([0.2, 0.8, 0.2])

    with abort:
        st.page_link("main.py", label="abort", icon="❌", use_container_width=True)
    
    with select_plot:
        st.write("hello world")
        #st.selectbox()
    

if __name__ == "__main__":
    show()