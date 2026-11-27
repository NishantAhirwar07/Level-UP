@echo off
if not exist venv\Scripts\python.exe python -m venv venv
call venv\Scripts\activate
python -m pip install -r requirements.txt
python -m flask --app app init-db
python app.py
pause
