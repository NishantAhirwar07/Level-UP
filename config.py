import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


def database_url():
    url = os.environ.get('DATABASE_URL')
    if not url:
        return f"sqlite:///{BASE_DIR / 'instance' / 'lifeflow.db'}"

    # Render and some hosted providers still supply the legacy postgres:// scheme.
    if url.startswith('postgres://'):
        url = 'postgresql://' + url[len('postgres://'):]

    # Use psycopg 3 explicitly; this project installs psycopg[binary].
    if url.startswith('postgresql://'):
        url = 'postgresql+psycopg://' + url[len('postgresql://'):]

    return url


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-only-change-this-secret-before-deployment')
    SQLALCHEMY_DATABASE_URI = database_url()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SECURE = os.environ.get('COOKIE_SECURE', '0') == '1'
    PERMANENT_SESSION_LIFETIME = 60 * 60 * 12
    MAX_CONTENT_LENGTH = 2 * 1024 * 1024
    RATELIMIT_DEFAULT = '200 per day;50 per hour'
