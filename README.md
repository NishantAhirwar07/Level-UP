# LifeFlow

LifeFlow is a Flask personal organizer for tasks, habits, income, expenses and budgets. It uses SQLite by default for local development and also supports PostgreSQL through the `DATABASE_URL` environment variable.

## Windows setup

```bat
python -m venv venv
venv\Scripts\activate
python -m pip install -r requirements.txt
python -m flask --app app init-db
python app.py
```

Open http://127.0.0.1:5000.

## Deploy to Render (Free Web Service)

This repository includes a `render.yaml` Blueprint. In Render, choose **New + → Blueprint**, connect this GitHub repository, and apply the Blueprint.

The service uses:
- Build command: `pip install -r requirements.txt`
- Start command: `python -m flask --app app init-db && gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --threads 2`
- Health check: `/health`
- A Render-generated `SECRET_KEY` and secure session cookies over HTTPS.

### Important: SQLite on Render Free is temporary

The default database is `instance/lifeflow.db`. Render Free Web Services have an ephemeral filesystem and do not support a persistent disk. SQLite will work for a demonstration, but its data can be lost when the service is restarted, redeployed, or spun down. Re-running `init-db` creates missing tables; it does **not** restore lost records or back up the database.

Do not use the free SQLite deployment for real users or important personal/financial records.

### More durable free setup: external PostgreSQL

For data that should survive Render service restarts and deploys, create a database with a separate provider that offers a free PostgreSQL tier, then set the Render service environment variable:

- `DATABASE_URL`: the provider's PostgreSQL connection string (use its pooled/SSL connection string if the provider recommends it).

The app normalizes common `postgres://` URLs and uses the installed Psycopg 3 driver. The dashboard's monthly date filters are database-agnostic. External free database plans have their own quotas, sleep/compute limits, and retention policies; check the provider's current terms and keep independent backups.

If `DATABASE_URL` is not set, the app falls back to local SQLite. Changing from SQLite to PostgreSQL does not automatically migrate existing user data; export/import or a migration is required.

## Tests

```bash
python -m pytest
```

## Security and operational notes

- Set a strong, persistent `SECRET_KEY`; the Render Blueprint generates one.
- `COOKIE_SECURE=1` is enabled in the Render Blueprint for HTTPS.
- Recovery codes are displayed once and stored only as hashes.
- The in-memory rate limiter is not shared across instances and resets when the process restarts. This is acceptable only for a small demo; use a shared rate-limit backend for a production deployment.
- `init-db` creates missing tables. It is not a schema migration system; use Alembic/Flask-Migrate before future schema changes.
- The app uses public CDNs for Bootstrap and Chart.js, so browser internet access is required unless assets are downloaded locally.
