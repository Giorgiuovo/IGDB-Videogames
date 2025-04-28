@echo off

REM Relativer Pfad zum Batch-Skript
set "BASE_DIR=%~dp0"

REM Ordner erstellen
mkdir "%BASE_DIR%data\presets"

REM JSON-Datei mit {} erstellen
echo {} > "%BASE_DIR%\data\presets\Unsaved preset.json"

REM Start Streamlit
start cmd /k "streamlit run Home.py"

REM Wait for server initialisation
timeout /t 5 /nobreak > NUL