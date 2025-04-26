@echo off
REM Start Streamlit
start cmd /k "streamlit run Home.py"

REM Wait for server initialisation
timeout /t 5 /nobreak > NUL