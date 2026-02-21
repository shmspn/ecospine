from app.extensions import db
from datetime import datetime, timezone
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import case, cast, Integer

class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    price = db.Column(db.Integer, nullable=False, default=0)
    size = db.Column(db.String(20), nullable=False)
    description = db.Column(db.Text, nullable=False)
    # image = db.Column(db.String(255))
    discount_percent = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    images = db.relationship(
        "ProductImage",
        back_populates="product",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    @hybrid_property
    def final_price(self):
        d = self.discount_percent or 0
        return int(self.price * (100 - d) / 100)

    @final_price.expression
    def final_price(cls):
        # discount null bo'lsa 0 deb olamiz
        d = case((cls.discount_percent.is_(None), 0), else_=cls.discount_percent)
        # integer natija chiqishi uchun cast
        return cast(cls.price * (100 - d) / 100, Integer)

