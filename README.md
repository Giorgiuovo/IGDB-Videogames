# SELECT * FROM games

SELECT * FROM games is a local-first data visualization app for exploring and analyzing video game data fetched from the IGDB API. It combines a fully configurable SQL query engine with interactive Plotly charts – all inside a Streamlit interface.

## Features

- Filtered data import from IGDB
- Local SQLite storage
- Interactive visualization UI with:
  - Line, Pie, Scatter, and Box plots
  - Custom X/Y axes, value settings, and labels
  - SQL-style filters: WHERE, GROUP BY, ORDER BY, AGGREGATE, HAVING
  - Plot-specific options like trendlines for LineCharts
- Multiple plots can be rendered at once
- Presets: Save and load entire plot configurations (as JSON)
- Modular design: Code separated by API, data, DB, visualization, etc.

## Technologies Used

- Python
- Streamlit
- Plotly
- SQLite
- Pandas
- NumPy
- Requests

## Setup Instructions

### 1. Get IGDB API Access

Create a Twitch developer account and register your IGDB application. Then:

- Copy `igdb_api_config_example.py` to `igdb_api_config.py`
- Fill in your `client_id` and `client_secret`

### 2. Download and Setup Data

Run the setup script to download data from IGDB and store it locally:

```bash
python setup_db.py
```

You’ll be guided through a CLI process to select and filter the data you want to import.

### 3. Install Requirements

```bash
pip install -r requirements.txt
```

### 4. Start the App

Run either of the following:

```bash
initialiser.bat
```

or

```bash
streamlit run Home.py
```

## Using the App

1. Go to the Add Plot page (link at the bottom of the homepage).
2. Choose one of four available plot types.
3. Configure the chart:
   - Axes and value fields
   - SQL options: WHERE, GROUP BY, ORDER BY, AGGREGATE, HAVING
   - Custom labels and chart-specific options
4. Click "Add Plot" to return to the homepage where your configured chart is rendered.
5. Repeat to add more plots. Charts are displayed below each other.

Configurations can be saved as presets (JSON files), allowing you to reload full setups later. There's no limit to how many presets or charts you can use, but rendering too many at once may reduce performance due to the complexity of Plotly visualizations.

## Project Structure (Overview)

```
api/            - IGDB API access and logic
data/           - Raw and filtered data files
db/             - Database setup and mapping
pages/          - Streamlit pages (Home, Add Plot, etc.)
visualization/  - Chart logic and JSON-based plot system
web/            - Preset handling, config tools, helpers
config.py       - Shared config
igdb_api_config.py - IGDB credentials (not tracked)
requirements.txt   - Required packages
```

## Requirements

- Twitch Developer credentials (IGDB API)
- Local SQLite database (generated via setup_db.py)

---

Feel free to fork, modify, and improve.  
