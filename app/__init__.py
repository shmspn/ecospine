from flask import Flask
from config import Config
from app.extensions import db
from flask_wtf.csrf import CSRFProtect
import os

csrf = CSRFProtect()

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)

    db.init_app(app)
    csrf.init_app(app)

    # routes
    from app.routes.home import home_bp
    from app.routes.admin import admin_bp

    app.register_blueprint(home_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')

    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

    app.config["UPLOAD_FOLDER"] = os.path.join(BASE_DIR, "static", "uploads")

    @app.template_filter("uzs")
    def uzs(value):
        try:
            return f"{int(value):,}".replace(",", " ")
        except (ValueError, TypeError):
            return value

    return app
