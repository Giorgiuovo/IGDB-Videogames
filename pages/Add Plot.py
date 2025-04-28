import streamlit as st
import json
import time
import config

def validate_config(plot_config, query_config, combined_plot_params, combined_query_params):
    """
    Checks:
    1. whether all required values are set (Plot + Query)
    2. whether HAVING is used without aggregation

    Args:
        plot_config (dict): user input for the plot
        query_config (dict): user input for the query
        combined_plot_params (dict): the merged plot parameters (including basic ones)
        combined_query_params (dict): the merged query parameters (including basic ones)

    Returns:
        list: list of error messages (empty list = everything is fine)
    """
    errors = []

    # Check required Plot-fields
    for param, options in combined_plot_params.items():
        if options.get("required"):
            value = plot_config.get(param)
            if value in (None, "", [], {}):
                errors.append(f"Plot: '{options['label']}' ist erforderlich!")

    # Check required Query-fields
    for param, options in combined_query_params.items():
        if options.get("required"):
            value = query_config.get(param)
            if value in (None, "", [], {}):
                errors.append(f"Query: '{options['label']}' ist erforderlich!")

    # Check HAVING without aggregation
    if query_config.get("having") and not query_config.get("aggregation"):
        errors.append("HAVING kann nur verwendet werden, wenn auch eine Aggregation gesetzt ist.")

    return errors

def clean_config(config):
    if isinstance(config, dict):
        return {k: clean_config(v) for k, v in config.items() if v not in (None, "", [], {}, 0, False)}
    elif isinstance(config, list):
        return [clean_config(item) for item in config if item not in (None, "", [], {}, 0, False)]
    else:
        return config

def translate_webname(select_box: str, whitelist: dict) -> str:
    """Translate webname to field name using whitelist"""
    return next((k for k, v in whitelist.items() if v["webname"] == select_box), None)

def render_filter_selector(plot_query: str, param: str, whitelist: dict, whitelisted_webnames: list):
    """Render filter selector UI components"""
    select_box = st.selectbox("Select field", whitelisted_webnames, key=f"{plot_query}_{param}")
    field = translate_webname(select_box, whitelist)
    
    if field:
        allowed_ops = whitelist[field]["operators"] 
        op = st.selectbox("Select operator", allowed_ops, key=f"{plot_query}_{param}_operator")
        
        value_type = whitelist[field]["type"]
        value = None

        if op == "BETWEEN":
            if value_type in ["int", "float"]:
                val1 = st.number_input("Value (from)", key=f"{plot_query}_{param}_{field}_between_1")
                val2 = st.number_input("Value (to)", key=f"{plot_query}_{param}_{field}_between_2")
                value = [val1, val2]
            elif value_type == "datetime":
                date1 = st.date_input("Date (from)", key=f"{plot_query}_{param}_{field}_between_1")
                date2 = st.date_input("Date (to)", key=f"{plot_query}_{param}_{field}_between_2")
                value = [str(date1), str(date2)]
        else:
            if value_type == "int":
                value = st.number_input("Value", step=1, key=f"{field}_val")
            elif value_type == "float":
                value = st.number_input("Value", format="%.2f", key=f"{field}_val")
            elif value_type == "str":
                value = st.text_input("Value", key=f"{field}_val")
            elif value_type == "datetime":
                value = str(st.date_input("Date", key=f"{field}_val"))

        if st.button("Add filter", key=f"add_filter_{field}"):
            if value is not None:
                if "filters" not in st.session_state:
                    st.session_state.filters = []
                st.session_state.filters.append({
                    "field": field,
                    "op": op,
                    "value": value
                })
                st.success("Filter added!")
            else:
                st.error("Please enter valid values!")

    # Display current filters
    st.markdown("#### Current filters:")
    if "filters" in st.session_state and st.session_state.filters:
        for i, f in enumerate(st.session_state.filters):
            cols = st.columns([0.7, 0.3])
            with cols[0]:
                field_info = whitelist.get(f['field'], {})
                webname = field_info.get('webname', f['field'])
                st.write(f"{webname} {f['op']} {f['value']}")
            with cols[1]:
                if st.button(f"Remove {i+1}", key=f"remove_filter_{i}"):
                    st.session_state.filters.pop(i)
                    st.rerun()
    else:
        st.info("No filters added yet.")

def render_sort_selector(param: str, whitelist: dict, whitelisted_webnames: list):
    """Render sort selector UI components"""
    if "sort_fields" not in st.session_state:
        st.session_state.sort_fields = []
    
    # Add new sort field
    col1, col2, col3 = st.columns([0.4, 0.3, 0.3])
    with col1:
        new_sort_field = st.selectbox("Sort field", whitelisted_webnames, key=f"new_sort_field_{param}")
    with col2:
        new_sort_direction = st.selectbox("Direction", ["ASC", "DESC"], key=f"new_sort_direction_{param}")
    with col3:
        if st.button("Add sort field", key=f"add_sort_field_{param}"):
            if new_sort_field != "---Please select---":
                field_name = translate_webname(new_sort_field, whitelist)
                st.session_state.sort_fields.append({
                    "field": field_name,
                    "direction": new_sort_direction
                })
                st.rerun()
    
    # Display current sort fields
    if st.session_state.sort_fields:
        st.markdown("**Current sort order:**")
        for i, sort_field in enumerate(st.session_state.sort_fields):
            cols = st.columns([0.7, 0.3])
            with cols[0]:
                st.write(f"{i+1}. {sort_field['field']} ({sort_field['direction']})")
            with cols[1]:
                if st.button(f"Remove {i+1}", key=f"remove_sort_{i}"):
                    st.session_state.sort_fields.pop(i)
                    st.rerun()

def render_aggregation_selector(param: str, options: dict, whitelist: dict, whitelisted_webnames: list):
    """Render aggregation selector with optional HAVING clause"""
    if "aggregation_havings" not in st.session_state:
        st.session_state.aggregation_havings = []
    
    # Aggregation Field Selection
    select_box = st.selectbox("Select field", whitelisted_webnames, key=f"agg_field_{param}")
    aggregation_function = st.selectbox("Function", 
                                      ["---Please select---", "COUNT", "SUM", "AVG", "MIN", "MAX"], 
                                      key=f"agg_func_{param}")
    
    if select_box != "---Please select---" and aggregation_function != "---Please select---":
        aggregation_field = translate_webname(select_box, whitelist)
        
        # HAVING Section (only shown if aggregation is selected)
        if "parameters" in options and "having" in options["parameters"]:
            st.markdown("##### Having condition (optional)")
            having_op = st.selectbox("Operator", 
                                         ["---Please select---"] + ["=", ">", "<", ">=", "<=", "BETWEEN"], 
                                         key=f"having_op_{param}")
            
            if having_op != "---Please select---":
                having_value = st.number_input("Value", step=1, key=f"having_val_{param}")
        
        # Add buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Add aggregation", key=f"add_agg_{param}"):
                st.session_state.aggregation_havings.append({
                    "aggregation": {
                        "field": aggregation_field,
                        "function": aggregation_function
                    }
                })
                st.success("Aggregation added!")
                st.rerun()
        
        if "parameters" in options and "having" in options["parameters"]:
            with col2:
                if st.button("Add with HAVING", key=f"add_agg_having_{param}"):
                    if having_op != "---Please select---" and "having_value" in locals():
                        st.session_state.aggregation_havings.append({
                            "aggregation": {
                                "field": aggregation_field,
                                "function": aggregation_function
                            },
                            "having": {
                                "field": aggregation_field,
                                "op": having_op,
                                "value": having_value
                            }
                        })
                        st.success("Aggregation with HAVING added!")
                        st.rerun()
                    else:
                        st.error("Please set valid HAVING condition")
    
    # Show current aggregations
    st.markdown("#### Current aggregations:")
    if st.session_state.aggregation_havings:
        for i, entry in enumerate(st.session_state.aggregation_havings):
            cols = st.columns([0.7, 0.3])
            with cols[0]:
                agg = entry["aggregation"]
                if "having" in entry:
                    having = entry["having"]
                    st.write(f"{agg['function']}({agg['field']}) HAVING {having['op']} {having['value']}")
                else:
                    st.write(f"{agg['function']}({agg['field']})")
            with cols[1]:
                if st.button(f"Remove {i+1}", key=f"remove_agg_{i}"):
                    st.session_state.aggregation_havings.pop(i)
                    st.rerun()
    else:
        st.info("No aggregations added yet.")

def render_options(plot_query: str, combined_parameters: dict, whitelist: dict, whitelisted_webnames: list):
    """Render all options for plot or query configuration"""
    for param, options in combined_parameters[plot_query].items():
        st.markdown(f'#### {options["label"]}')
        
        if options["input_type"] == "text_input":
            st.text_input("", key=f"{plot_query}_{param}", label_visibility="collapsed")
            
        elif options["input_type"] == "number_input":
            st.number_input("", step=1, key=f"{plot_query}_{param}", label_visibility="collapsed")
            
        elif options["input_type"] == "checkbox":
            st.checkbox("", key=f"{plot_query}_{param}", label_visibility="collapsed")
            
        elif options["input_type"] == "field_selector":
            select_box = st.selectbox("", whitelisted_webnames, key=f"{plot_query}_{param}", label_visibility="collapsed")
            
        elif options["input_type"] == "field_list_selector":
            st.multiselect("", whitelisted_webnames, key=f"{plot_query}_{param}", label_visibility="collapsed")
            
        elif options["input_type"] == "filter_selector":
            render_filter_selector(plot_query, param, whitelist, whitelisted_webnames)
            
        elif options["input_type"] == "sort_selector":
            render_sort_selector(param, whitelist, whitelisted_webnames)
            
        elif options["input_type"] == "aggregation_selector":
            render_aggregation_selector(param, options, whitelist, whitelisted_webnames)

def show():
    # Initialize session state variables if they don't exist
    if "filters" not in st.session_state:
        st.session_state.filters = []
    if "aggregation_havings" not in st.session_state:
        st.session_state.aggregation_havings = []
    if "sort_fields" not in st.session_state:
        st.session_state.sort_fields = []

    # Load chart types
    with open(config.CHART_TYPES_PATH, "r", encoding="utf-8") as f:
        chart_types = json.load(f)["plots"]

    # Load whitelist
    with open(config.QUERY_WHITELIST_PATH, "r", encoding="utf-8") as f:
        whitelist = json.load(f)
        whitelisted_webnames = ["---Please select---"] + [field["webname"] for field in whitelist.values()]

    # UI Layout
    select_plot, middlespace, abort = st.columns([0.4, 0.4, 0.2])
    with abort:
        st.page_link("Home.py", label="abort", icon="❌", use_container_width=True)
    with select_plot:
        available_plot_types = [key for key in chart_types.keys() if key != "basic"]
        plot_type = st.selectbox(
            "Choose a plottype",
            options=available_plot_types,
            format_func=lambda x: chart_types[x]["web_name"],
            key="plot_type_select",
            index=None,
            placeholder = "---Please select---"
        )
    if plot_type:
        # Combine parameters
        basic_plot_params = chart_types["basic"]["parameters"].get("plot", {})
        basic_query_params = chart_types["basic"]["parameters"].get("query", {})
        selected_plot_params = chart_types[plot_type]["parameters"].get("plot", {})
        selected_query_params = chart_types[plot_type]["parameters"].get("query", {})

        combined_parameters = {
            "plot": {**basic_plot_params, **selected_plot_params},
            "query": {**basic_query_params, **selected_query_params}
        }

        # Render configuration sections
        with st.expander("Plot configuration"):
            render_options("plot", combined_parameters, whitelist, whitelisted_webnames)

        with st.expander("Query configuration"):
            render_options("query", combined_parameters, whitelist, whitelisted_webnames)

        # Build temp_config from session state
        temp_config = {
            "plot_type": plot_type,
            "plot_settings": {},
            "query_settings": {
                "filters": st.session_state.get("filters", []),
                "aggregation_havings": st.session_state.get("aggregation_havings", []),
                "sort_fields": st.session_state.get("sort_fields", []),
                "group_by": st.session_state.get("group_by", []),
                "limit": st.session_state.get("limit", None),
                "offset": st.session_state.get("offset", None)
            }
        }

        # Add simple fields to temp_config
        for param in combined_parameters["plot"]:
            if combined_parameters["plot"][param]["input_type"] in ["text_input", "number_input", "checkbox"]:
                temp_config["plot_settings"][param] = st.session_state.get(f"plot_{param}")
            elif combined_parameters["plot"][param]["input_type"] == "field_selector":
                temp_config["plot_settings"][param] = translate_webname(st.session_state.get(f"plot_{param}"), whitelist)

        for param in combined_parameters["query"]:
            if combined_parameters["query"][param]["input_type"] in ["text_input", "number_input", "checkbox"]:
                temp_config["query_settings"][param] = st.session_state.get(f"query_{param}")
            elif combined_parameters["query"][param]["input_type"] == "field_list_selector":
                temp_config["query_settings"][param] = [translate_webname(f, whitelist) 
                                                    for f in st.session_state.get(f"query_{param}", [])]

        # Preview and actions
        st.subheader("Preview of current configuration:")
        st.json(temp_config)

        if st.button("Reset"):
            for key in list(st.session_state.keys()):
                if key not in ["preset", "pos"]:  # Keep these for navigation
                    del st.session_state[key]
            st.rerun()

        if st.button("Save configuration and add to page"):
            # Validate required fields
            errors = []
            for param, options in combined_parameters["plot"].items():
                if options.get("required") and not temp_config["plot_settings"].get(param):
                    errors.append(f"Plot: '{options['label']}' is required!")
            
            for param, options in combined_parameters["query"].items():
                if options.get("required") and not temp_config["query_settings"].get(param):
                    errors.append(f"Query: '{options['label']}' is required!")

            if errors:
                for error in errors:
                    st.error(error)
            else:
                def append_to_json_file(path, key, new_entry):
                    try:
                        with open(path, "r", encoding="utf-8") as f:
                            data = json.load(f)
                    except (FileNotFoundError, json.JSONDecodeError):
                        data = {}

                    data[key] = new_entry

                    with open(path, "w", encoding="utf-8") as f:
                        json.dump(data, f, indent=4)

                clean_temp_config = clean_config(temp_config)
                append_to_json_file(
                    f"{config.PRESET_PATH}/{st.session_state.preset}.json",
                    st.session_state.pos,
                    clean_temp_config
                )
                st.success("Configuration saved!")
                time.sleep(1.2)
                del temp_config
                st.switch_page("Home.py")

if __name__ == "__main__":
    show()