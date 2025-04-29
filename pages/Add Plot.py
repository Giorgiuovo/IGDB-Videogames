import streamlit as st
import json
import time
import config
from typing import Optional, List, Dict, Any

def validate_config(plot_config: Dict[str, Any], query_config: Dict[str, Any]) -> List[str]:
    """
    Validates the plot and query configuration.
    
    Args:
        plot_config: Plot configuration dictionary
        query_config: Query configuration dictionary
        
    Returns:
        List of error messages (empty if valid)
    """
    errors = []
    
    # Check required plot fields
    if not plot_config.get("plot_type"):
        errors.append("Plot type is required")
        
    # Check if plot references aggregated fields that don't exist
    for k, v in plot_config.items():
        if isinstance(v, str) and v.startswith("agg:"):
            agg_alias = v[4:]
            if agg_alias not in query_config.get("aggregation", {}):
                errors.append(f"Plot references non-existent aggregation '{agg_alias}'")
        
    # Check required query fields
    if not query_config.get("fields"):
        errors.append("At least one field must be selected")
        
    # Check HAVING without aggregation
    if query_config.get("having") and not query_config.get("aggregation"):
        errors.append("HAVING can only be used with aggregation")
        
    return errors

def clean_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """Remove empty/None values from config"""
    return {k: v for k, v in config.items() if v not in (None, "", [], {}, 0, False)}

def translate_webname(select_box: str, whitelist: Dict[str, Any]) -> Optional[str]:
    """Translate webname to field name using whitelist"""
    return next((k for k, v in whitelist.items() if v.get("webname") == select_box), None)

def render_filter_selector(whitelist: Dict[str, Any]) -> None:
    """Render filter selector UI components"""
    # Field selection
    field_webname = st.selectbox(
        "Select field to filter",
        options=["---Select field---"] + [v["webname"] for v in whitelist.values()],
        key="filter_field_select"
    )
    
    if field_webname == "---Select field---":
        return
        
    field = translate_webname(field_webname, whitelist)
    field_info = whitelist[field]
    
    # Operator selection
    op = st.selectbox(
        "Select operator",
        options=field_info["operators"],
        key=f"filter_op_{field}"
    )
    
    # Value input based on type
    value = None
    if field_info["type"] == "int":
        value = st.number_input("Value", step=1, key=f"filter_value_{field}")
    elif field_info["type"] == "float":
        value = st.number_input("Value", format="%.2f", key=f"filter_value_{field}")
    elif field_info["type"] == "str":
        value = st.text_input("Value", key=f"filter_value_{field}")
    elif field_info["type"] == "datetime":
        value = str(st.date_input("Date", key=f"filter_value_{field}"))
    
    # Add filter button
    if st.button("Add filter", key=f"add_filter_{field}"):
        if "filters" not in st.session_state:
            st.session_state.filters = []
            
        st.session_state.filters.append({
            "field": field,
            "op": op,
            "value": value
        })
        st.rerun()
    
    # Display current filters
    st.subheader("Current Filters")
    if "filters" in st.session_state and st.session_state.filters:
        for i, f in enumerate(st.session_state.filters):
            cols = st.columns([0.8, 0.2])
            with cols[0]:
                st.write(f"{whitelist[f['field']]['webname']} {f['op']} {f['value']}")
            with cols[1]:
                if st.button("❌", key=f"remove_filter_{i}"):
                    st.session_state.filters.pop(i)
                    st.rerun()
    else:
        st.info("No filters added yet")

def render_sort_selector(whitelist: Dict[str, Any]) -> None:
    """Render sort selector UI components"""
    # Add new sort field
    col1, col2, col3 = st.columns([0.5, 0.3, 0.2])
    with col1:
        field_webname = st.selectbox(
            "Select field to sort",
            options=["---Select field---"] + [v["webname"] for v in whitelist.values()],
            key="sort_field_select"
        )
    with col2:
        direction = st.selectbox(
            "Direction",
            options=["ASC", "DESC"],
            key="sort_direction_select"
        )
    with col3:
        if st.button("Add sort", key="add_sort") and field_webname != "---Select field---":
            if "sort_fields" not in st.session_state:
                st.session_state.sort_fields = []
                
            st.session_state.sort_fields.append({
                "field": translate_webname(field_webname, whitelist),
                "direction": direction
            })
            st.rerun()
    
    # Display current sort fields
    st.subheader("Current Sort Order")
    if "sort_fields" in st.session_state and st.session_state.sort_fields:
        for i, sf in enumerate(st.session_state.sort_fields):
            cols = st.columns([0.8, 0.2])
            with cols[0]:
                st.write(f"{i+1}. {whitelist[sf['field']]['webname']} ({sf['direction']})")
            with cols[1]:
                if st.button("❌", key=f"remove_sort_{i}"):
                    st.session_state.sort_fields.pop(i)
                    st.rerun()
    else:
        st.info("No sort fields added yet")

def render_aggregation_selector(whitelist: Dict[str, Any]) -> None:
    """Render aggregation selector UI components"""
    col1, col2 = st.columns([0.6, 0.4])
    with col1:
        field_webname = st.selectbox(
            "Select field to aggregate",
            options=["---Select field---"] + [v["webname"] for v in whitelist.values()],
            key="agg_field_select"
        )
    with col2:
        func = st.selectbox(
            "Function",
            options=["COUNT", "SUM", "AVG", "MIN", "MAX"],
            key="agg_func_select"
        )

    if st.button("Add aggregation", key="add_agg") and field_webname != "---Select field---":
        if "aggregations" not in st.session_state:
            st.session_state.aggregations = {}

        field = translate_webname(field_webname, whitelist)
        # Automatically generate alias
        agg_alias = f"{func}_{field.split('.')[-1]}"

        st.session_state.aggregations[agg_alias] = {
            "field": field,
            "function": func
        }
        
        # Automatically add the aggregation field to query fields if not already present
        if "query_fields" not in st.session_state:
            st.session_state.query_fields = []
            
        if field not in st.session_state.query_fields:
            st.session_state.query_fields.append(field)
            
        st.rerun()
    
    # Display current aggregations
    st.subheader("Current Aggregations")
    if "aggregations" in st.session_state and st.session_state.aggregations:
        for alias, agg in st.session_state.aggregations.items():
            cols = st.columns([0.8, 0.2])
            with cols[0]:
                st.write(f"{alias}: {agg['function']}({whitelist[agg['field']]['webname']})")
            with cols[1]:
                if st.button("❌", key=f"remove_agg_{alias}"):
                    del st.session_state.aggregations[alias]
                    st.rerun()
    else:
        st.info("No aggregations added yet")

def render_having_selector() -> None:
    """Render HAVING condition selector"""
    if not st.session_state.get("aggregations"):
        st.info("Add aggregations first to use HAVING")
        return
        
    col1, col2, col3 = st.columns([0.4, 0.3, 0.3])
    with col1:
        agg_alias = st.selectbox(
            "Select aggregation",
            options=list(st.session_state.aggregations.keys()),
            key="having_agg_select"
        )
    with col2:
        op = st.selectbox(
            "Operator",
            options=["=", "!=", "<", "<=", ">", ">="],
            key="having_op_select"
        )
    with col3:
        value = st.number_input("Value", key="having_value")
    
    if st.button("Add HAVING condition", key="add_having"):
        if "having" not in st.session_state:
            st.session_state.having = []
            
        st.session_state.having.append({
            "aggregation": agg_alias,
            "op": op,
            "value": value
        })
        st.rerun()
    
    # Display current HAVING conditions
    st.subheader("Current HAVING Conditions")
    if "having" in st.session_state and st.session_state.having:
        for i, h in enumerate(st.session_state.having):
            cols = st.columns([0.8, 0.2])
            with cols[0]:
                st.write(f"{h['aggregation']} {h['op']} {h['value']}")
            with cols[1]:
                if st.button("❌", key=f"remove_having_{i}"):
                    st.session_state.having.pop(i)
                    st.rerun()
    else:
        st.info("No HAVING conditions added yet")

def show():
    # Initialize session state
    if "filters" not in st.session_state:
        st.session_state.filters = []
    if "sort_fields" not in st.session_state:
        st.session_state.sort_fields = []
    if "aggregations" not in st.session_state:
        st.session_state.aggregations = {}
    if "having" not in st.session_state:
        st.session_state.having = []
    if "query_fields" not in st.session_state:
        st.session_state.query_fields = []
    
    # Load chart types and whitelist
    with open(config.CHART_TYPES_PATH, "r", encoding="utf-8") as f:
        chart_types = json.load(f)["plots"]
    
    with open(config.QUERY_WHITELIST_PATH, "r", encoding="utf-8") as f:
        whitelist = json.load(f)
    
    # UI Layout
    st.title("Add New Plot")
    
    # Plot type selection
    plot_type = st.selectbox(
        "Select plot type",
        options=[k for k in chart_types.keys() if k != "basic"],
        format_func=lambda x: chart_types[x]["web_name"],
        key="plot_type_select",
        placeholder="---Please select---",
        index=None
    )
        
    if plot_type:
        # Get plot parameters
        plot_params = {**chart_types["basic"]["parameters"].get("plot", {}), 
                    **chart_types[plot_type]["parameters"].get("plot", {})}
        query_params = {**chart_types["basic"]["parameters"].get("query", {}), 
                    **chart_types[plot_type]["parameters"].get("query", {})}
        
        # Plot configuration
        with st.expander("Plot Configuration"):
            for param, options in plot_params.items():
                st.markdown(f"**{options['label']}**")
                
                if options["input_type"] == "text_input":
                    st.text_input("", key=f"plot_{param}", label_visibility="collapsed")
                elif options["input_type"] == "number_input":
                    st.number_input("", key=f"plot_{param}", label_visibility="collapsed")
                elif options["input_type"] == "checkbox":
                    st.checkbox("", key=f"plot_{param}", label_visibility="collapsed")
                elif options["input_type"] == "field_selector":
                    # Store the translated field name in a separate key
                    field_key = f"plot_{param}_field"
                    if field_key not in st.session_state:
                        st.session_state[field_key] = ""
                    
                    # Prepare options: normal fields + aggregated fields
                    field_options = ["---Select field---"] + [v["webname"] for v in whitelist.values()]
                    
                    # Add aggregated fields if any exist
                    if st.session_state.get("aggregations"):
                        agg_options = [f"agg:{alias}" for alias in st.session_state.aggregations.keys()]
                        field_options += agg_options
                    
                    field_webname = st.selectbox(
                        "",
                        options=field_options,
                        key=f"plot_{param}_select",
                        label_visibility="collapsed"
                    )
                    
                    # Update the field value only if a selection is made
                    if field_webname != "---Select field---":
                        if field_webname.startswith("agg:"):
                            # Handle aggregated field selection
                            st.session_state[field_key] = f"agg:{field_webname[4:]}"
                        else:
                            # Handle normal field selection
                            st.session_state[field_key] = translate_webname(field_webname, whitelist)
        
        # Query configuration
        with st.expander("Query Configuration"):
            # Fields selection
            selected_fields = st.multiselect(
                "Select fields to query",
                options=[v["webname"] for v in whitelist.values()],
                default=[whitelist[f]["webname"] for f in st.session_state.query_fields],
                key="query_fields_select"
            )
            
            # Store the translated fields in query_fields
            st.session_state.query_fields = [translate_webname(f, whitelist) for f in selected_fields]

            group_by_fields = st.multiselect(
                "Group by fields",
                options=[v["webname"] for v in whitelist.values()],
                key="query_group_by_fields"
            )
            st.session_state.query_group_by = [translate_webname(f, whitelist) for f in group_by_fields]
            
            # Query options
            render_filter_selector(whitelist)
            render_sort_selector(whitelist)
            render_aggregation_selector(whitelist)
            render_having_selector()
            
            # Limit/offset
            col1, col2 = st.columns(2)
            with col1:
                limit = st.number_input("Limit", min_value=0, step=1, key="query_limit")
            with col2:
                offset = st.number_input("Offset", min_value=0, step=1, key="query_offset")
        
        # Build config object
        config_obj = {
            "plot_type": plot_type,
            "plot_settings": {
                param: st.session_state.get(f"plot_{param}_field") if options["input_type"] == "field_selector" 
                    else st.session_state.get(f"plot_{param}")
                for param, options in plot_params.items()
            },
            "query_settings": {
                "fields": st.session_state.query_fields,
                "filters": st.session_state.get("filters", []),
                "sort_fields": st.session_state.get("sort_fields", []),
                "aggregation": st.session_state.get("aggregations", {}),
                "having": st.session_state.get("having", []),
                "group_by": st.session_state.get("query_group_by", []),
                "limit": st.session_state.get("query_limit"),
                "offset": st.session_state.get("query_offset")
            }
        }
        
        # Clean and preview config
        clean_config_obj = clean_config(config_obj)
        st.subheader("Configuration Preview")
        st.json(clean_config_obj)
        
        # Action buttons
        col1, col2, col3 = st.columns([0.2, 0.2, 0.6])
        with col1:
            if st.button("Reset"):
                for key in list(st.session_state.keys()):
                    if key not in ["preset", "pos"]:  # Preserve navigation state
                        del st.session_state[key]
                st.rerun()
        
        with col2:
            if st.button("Save"):
                errors = validate_config(
                    {"plot_type": clean_config_obj.get("plot_type"), **clean_config_obj["plot_settings"]},
                    clean_config_obj["query_settings"]
                )

                if errors:
                    for error in errors:
                        st.error(error)
                else:
                    # Save to preset
                    with open(f"{config.PRESET_PATH}/{st.session_state.preset}.json", "r+", encoding="utf-8") as f:
                        presets = json.load(f)
                        presets[st.session_state.pos] = clean_config_obj
                        f.seek(0)
                        json.dump(presets, f, indent=4)
                        f.truncate()
                    
                    st.success("Plot saved successfully!")
                    time.sleep(1)
                    st.switch_page("Home.py")

if __name__ == "__main__":
    show()