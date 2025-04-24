@echo off
cd /d "%~dp0"

REM Check if the virtual environment exists
if not exist "env\Scripts\activate" (
    echo Virtual environment not found. Creating one...
    python -m venv env
)

REM Activate the virtual environment
call "env\Scripts\activate" || (echo Failed to activate the virtual environment & pause & exit /b)

REM Run Streamlit
streamlit run main.py || (echo Failed to run Streamlit & pause & exit /b)

pause