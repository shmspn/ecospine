import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    # Use environment variables in production; keep a safe default for development.
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key')

    # Allow overriding the DB URL with DATABASE_URL env var (12-factor style).
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'sqlite:///' + os.path.join(BASE_DIR, 'instance', 'ecospine.db')
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False
