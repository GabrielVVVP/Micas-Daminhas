@echo off
cd /d "%~dp0"

REM Step 4: Create a virtual environment
python -m venv env

REM Step 5: Activate the virtual environment
call "env\Scripts\activate"

REM Step 6: Install dependencies
pip install -r requirements.txt