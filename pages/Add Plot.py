import streamlit as st
import json
import config

def validate_config(plot_config, query_config, combined_plot_params, combined_query_params):
    """
    Prüft:
    1. ob alle required Werte gesetzt sind (Plot + Query)
    2. ob HAVING ohne Aggregation gesetzt wurde

    Args:
        plot_config (dict): User-Eingaben für Plot
        query_config (dict): User-Eingaben für Query
        combined_plot_params (dict): die zusammengeführten Plot-Parameter (inkl. basic)
        combined_query_params (dict): die zusammengeführten Query-Parameter (inkl. basic)

    Returns:
        list: Liste der Fehlertexte (leere Liste = alles ok)
    """

    errors = []

    # --- Check 1: Required Plot-Fields ---
    for param, options in combined_plot_params.items():
        if options.get("required"):
            value = plot_config.get(param)
            if value in (None, "", [], {}):  # Leere Werte abfangen
                errors.append(f"Plot: '{options['label']}' ist erforderlich!")

    # --- Check 2: Required Query-Fields ---
    for param, options in combined_query_params.items():
        if options.get("required"):
            value = query_config.get(param)
            if value in (None, "", [], {}):
                errors.append(f"Query: '{options['label']}' ist erforderlich!")

    # --- Check 3: HAVING ohne Aggregation ---
    if query_config.get("having") and not query_config.get("aggregation"):
        errors.append("HAVING kann nur verwendet werden, wenn auch eine Aggregation gesetzt ist.")

    return errors


def show():
    temp_config = {
        "plot_type": None,
        "plot_settings": {},
        "query_settings": {
            "filters": [],
            "group_by": [],
            "aggregation": {},
            "having": {},
            "limit": None,
            "offset": None
        }
    }

    select_plot, middlespace, abort = st.columns([0.2, 0.8, 0.2])

    with abort:
        st.page_link("Home.py", label="abort", icon="❌", use_container_width=True, )
    with select_plot:
        with open(config.CHART_TYPES_PATH, "r", encoding = "utf-8") as f:
            chart_types = json.load(f)["plots"]

        available_plot_types = [key for key in chart_types.keys() if key != "basic"]
        plot_type = st.selectbox(
        "Choose a plottype",
        options=available_plot_types,
        format_func=lambda x: chart_types[x]["web_name"],
        )
        temp_config["plot_type"] = plot_type

    # Immer das Basic mit reinnehmen:
    basic_plot_params = chart_types["basic"]["parameters"].get("plot", {})
    basic_query_params = chart_types["basic"]["parameters"].get("query", {})

    # Und den gewählten Typ:
    selected_plot_params = chart_types[plot_type]["parameters"].get("plot", {})
    selected_query_params = chart_types[plot_type]["parameters"].get("query", {})

    # Jetzt einfach zusammenführen (Basic + spezifischer Typ):
    combined_parameters = {
    "plot": {**basic_plot_params, **selected_plot_params},
    "query": {**basic_query_params, **selected_query_params}
    }


    
    with st.expander("Plot configuration"):
        for param, options in combined_parameters["plot"].items():
            if options["input_type"] == "text_input":
                temp_config["plot_settings"][param] = st.text_input(options["label"])
            elif options["input_type"] == "number_input":
                temp_config["plot_settings"][param] = st.number_input(options["label"])
            elif options["input_type"] == "checkbox":
                temp_config["plot_settings"][param] = st.checkbox(options["label"])
            elif options["input_type"] == "field_selector":
                with open(config.QUERY_WHITELIST_PATH, "r", encoding="utf-8") as f:
                    whitelist = json.load(f)
                    whitelisted_fields = list(whitelist.keys())
                    whitelisted_webnames = ["---Please select---"] + [field["webname"] for field in whitelist.values()]
                temp_config["plot_settings"][param] = st.selectbox(options["label"], whitelisted_webnames)

    with st.expander("Query configuration"):

        # --- FILTER ---
        st.markdown("### Filter hinzufügen")
        field = st.selectbox("Feld auswählen", whitelisted_webnames)
        
        if field != "— Bitte wählen —":
            allowed_ops = whitelisted_fields["operators"]
            operator = st.selectbox("Operator auswählen", allowed_ops)
            value_type = whitelisted_fields[field]["type"]

            if operator == "BETWEEN":
                if value_type in ["int", "float"]:
                    val1 = st.number_input("Wert (von)", key=f"{field}_between_1")
                    val2 = st.number_input("Wert (bis)", key=f"{field}_between_2")
                    value = [val1, val2]
                elif value_type == "datetime":
                    date1 = st.date_input("Datum (von)", key=f"{field}_between_1")
                    date2 = st.date_input("Datum (bis)", key=f"{field}_between_2")
                    value = [str(date1), str(date2)]
                else:
                    st.error("BETWEEN nur für Zahlen oder Datumswerte!")
                    value = None
            else:
                if value_type == "int":
                    value = st.number_input("Wert", step=1, key=f"{field}_val")
                elif value_type == "float":
                    value = st.number_input("Wert", format="%.2f", key=f"{field}_val")
                elif value_type == "str":
                    if operator == "IN":
                        value = st.text_input("Mehrere Werte (kommagetrennt)").split(",")
                    else:
                        value = st.text_input("Wert")
                elif value_type == "datetime":
                    value = str(st.date_input("Datum", key=f"{field}_val"))
                else:
                    value = None

            if st.button("Filter hinzufügen"):
                if value is not None:
                    temp_config["query_settings"]["filters"].append({
                        "field": field,
                        "operator": operator,
                        "value": value
                    })
                    st.success("Filter hinzugefügt!")
                else:
                    st.error("Bitte gültige Werte eingeben!")

        # --- Bestehende Filter anzeigen und löschen ---
        st.markdown("### Aktuelle Filter:")
        if temp_config["query_settings"]["filters"]:
            for idx, f in enumerate(temp_config["query_settings"]["filters"]):
                st.write(f"{f['field']} {f['operator']} {f['value']}")
                if st.button(f"Filter {idx+1} entfernen", key=f"remove_filter_{idx}"):
                    temp_config["query_settings"]["filters"].pop(idx)
                    st.experimental_rerun()
        else:
            st.info("Noch keine Filter hinzugefügt.")

        # --- GROUP BY ---
        st.markdown("### Group By")
        temp_config["query_settings"]["group_by"] = st.multiselect("Group By Felder", list(whitelisted_webnames))

        # --- AGGREGATION ---
        st.markdown("### Aggregation")
        aggregation_field = st.selectbox("Feld für Aggregation", ["— Bitte wählen —"] + list(whitelisted_webnames))
        aggregation_function = st.selectbox("Funktion", ["— Bitte wählen —", "COUNT", "SUM", "AVG", "MIN", "MAX"])
        if aggregation_field != "— Bitte wählen —" and aggregation_function != "— Bitte wählen —":
            temp_config["query_settings"]["aggregation"] = {
                "field": aggregation_field,
                "function": aggregation_function
            }

        # --- HAVING ---
        st.markdown("### Having (optional)")
        having_field = st.selectbox("Having-Feld auswählen", ["— Bitte wählen —"] + list(whitelisted_webnames))
        if having_field != "— Bitte wählen —":
            having_ops = whitelisted_fields[having_field]["operators"]
            having_operator = st.selectbox("Having-Operator", having_ops)
            having_value_type = whitelisted_fields[having_field]["type"]

            if having_value_type == "int":
                having_value = st.number_input("Wert", step=1, key="having_val")
            elif having_value_type == "float":
                having_value = st.number_input("Wert", format="%.2f", key="having_val")
            elif having_value_type == "str":
                having_value = st.text_input("Wert")
            elif having_value_type == "datetime":
                having_value = str(st.date_input("Datum"))
            else:
                having_value = None

            temp_config["query_settings"]["having"] = {
                "field": having_field,
                "operator": having_operator,
                "value": having_value
            }

        # --- LIMIT / OFFSET ---
        st.markdown("### Limit & Offset")
        temp_config["query_settings"]["limit"] = st.number_input("Limit", min_value=0, step=1)
        temp_config["query_settings"]["offset"] = st.number_input("Offset", min_value=0, step=1)
    
    st.subheader("Vorschau der aktuellen Konfiguration:")
    st.json(temp_config)
    if st.button("Konfiguration übernehmen und speichern"):
        with open(config.UNSAVED_PRESET_PATH, "w", encoding="utf-8") as f:
            json.dump(temp_config, f, indent=4)
        st.success("Konfiguration gespeichert!")

    if st.button("Zurücksetzen"):
        temp_config["plot_type"] = None
        temp_config["plot_settings"] = {}
        temp_config["query_settings"] = {
            "filters": [],
            "group_by": [],
            "aggregation": {},
            "having": {},
            "limit": None,
            "offset": None
        }
        st.warning("Temp-Konfiguration zurückgesetzt!")
        st.experimental_rerun()
    

if __name__ == "__main__":
    show()