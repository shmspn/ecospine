import os

from app import create_app
from app.extensions import db
from flask_migrate import Migrate

app = create_app()

migrate = Migrate(app, db)

# Only create all tables automatically in testing or when explicitly requested.
# When using Flask-Migrate/Alembic in normal development/production, rely on migrations.
with app.app_context():
    if app.config.get('TESTING') or os.environ.get('CREATE_ALL') == '1':
        db.create_all()

if __name__ == '__main__':
    app.run(port=4000)
