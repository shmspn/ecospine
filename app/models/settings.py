from datetime import datetime, timezone
from app.extensions import db

class Settings(db.Model):
    __tablename__ = 'settings'

    id = db.Column(db.Integer, primary_key=True)
    usd_to_uzs = db.Column(db.Integer, nullable=False, default=12500)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))