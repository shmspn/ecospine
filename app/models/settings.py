from datetime import datetime
from app.extensions import db

class Settings(db.Model):
    __tablename__ = 'settings'

    id = db.Column(db.Integer, primary_key=True)
    usd_to_uzs = db.Column(db.Integer, nullable=False, default=12500)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)