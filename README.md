# Eco Spine — Quick start

Short instructions to run the project locally and set required environment variables.

1) Create and activate a virtual environment

```bash
python -m venv venv
source venv/bin/activate
```

2) Install dependencies

```bash
pip install -r requirements.txt
```

If you plan to use database migrations, ensure `Flask-Migrate` is installed (it's included in `requirements.txt`).

3) Environment variables

Set a secure `SECRET_KEY` and (optionally) the database URL. Defaults exist for development.

```bash
# set a strong secret key
export SECRET_KEY="your-strong-secret"

# By default the app uses a local SQLite file under instance/ecospine.db
# To override and use Postgres (example):
export DATABASE_URL="postgresql://user:pass@localhost:5432/ecospine"

# Only needed if you want the app to auto-create tables on startup
export CREATE_ALL=1
```

4) Run the app

```bash
python run.py
```

5) Using Flask-Migrate (optional)

```bash
# tell Flask CLI where the app is
export FLASK_APP=run.py

# one-time init (if migrations/ not present)
flask db init

# create migration from models
flask db migrate -m "Initial"

# apply migrations
flask db upgrade
```

Notes
- In production always provide a real `SECRET_KEY` via env variables.
- Prefer setting `DATABASE_URL` to a managed DB (Postgres/MySQL) for production.
