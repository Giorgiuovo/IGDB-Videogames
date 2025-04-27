import inspect
import visualization.plots as plots

def unpack_aggregation_havings(agg_having_list):
    aggregations = []
    havings = []

    if agg_having_list:
        for entry in agg_having_list:
            if "aggregation" in entry:
                aggregations.append(entry["aggregation"])
            if "having" in entry:
                havings.append(entry["having"])
    
    return aggregations if aggregations else None, havings if havings else None

def create_plot_object(plot_config, conn, cursor):
    plot_type = plot_config.get("plot_type")
    settings = plot_config.get("plot_settings", {})
    query = plot_config.get("query_settings", {})

    # Extract and transform aggregation_havings into separate aggregation and having arguments
    agg_having_list = query.pop("aggregation_havings", None)
    aggregation, having = unpack_aggregation_havings(agg_having_list)

    # Mapping of plot types to their corresponding classes
    plot_classes = {
        "line_chart": plots.line_chart,
        # Add more plot types here as needed (e.g., "bar_chart": plots.bar_chart)
    }

    plot_class = plot_classes.get(plot_type)
    if not plot_class:
        raise ValueError(f"Unsupported plot type: {plot_type}")

    # Inspect the __init__ signature of the plot class to get valid parameters
    sig = inspect.signature(plot_class.__init__)
    valid_params = set(sig.parameters.keys()) - {"self"}

    # Combine plot_settings and query_settings, and add unpacked aggregation/having
    combined_config = {
        "conn": conn,
        "cursor": cursor,
        **settings,
        **query,
        "aggregation": aggregation,
        "having": having
    }

    # Filter out any parameters that the class does not accept
    init_args = {k: v for k, v in combined_config.items() if k in valid_params}

    # Instantiate and return the plot object
    return plot_class(**init_args)