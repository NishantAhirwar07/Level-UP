# LifeFlow

LifeFlow is a Flask + SQLite personal organizer for tasks, habits, income, expenses and budgets.

## Windows setup
```bat
python -m venv venv
venv\Scripts\activate
python -m pip install -r requirements.txt
python -m flask --app app init-db
python app.py
```
Open http://127.0.0.1:5000.

Set `SECRET_KEY` in the environment before deployment. The database is `instance/lifeflow.db`; initialization creates only missing tables and never deletes existing data.

## Tests
```bash
python -m pytest
```

## Limitations
This project uses public CDNs for Bootstrap and Chart.js, so internet access is required unless assets are downloaded locally. Recovery codes are displayed once and stored only as hashes. Configure HTTPS and a persistent production secret/rate-limit store for deployment.
