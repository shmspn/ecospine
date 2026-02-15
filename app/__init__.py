from flask import Flask
from config import Config
from app.extentions import db

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)

    db.init_app(app)

    # routes
    from app.routes.home import home_bp
    from app.routes.admin import admin_bp

    app.register_blueprint(home_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')

    @app.template_filter("uzs")
    def uzs(value):
        try:
            return f"{int(value):,}".replace(",", " ")
        except Exception:
            return value

    return app
