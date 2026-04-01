from datetime import datetime, timezone
from app import db


class Product(db.Model):
    __tablename__ = "products"

    id            = db.Column(db.Integer, primary_key=True)
    name          = db.Column(db.String(200), nullable=False)
    description   = db.Column(db.Text,        nullable=True)
    price         = db.Column(db.Numeric(10, 2), nullable=False)
    original_price = db.Column(db.Numeric(10, 2), nullable=True)
    discount      = db.Column(db.Integer,  nullable=True)       # percentage
    image_url     = db.Column(db.String(500), nullable=True)
    occasion      = db.Column(db.String(50),  nullable=True)    # Wedding, Festival…
    fabric        = db.Column(db.String(50),  nullable=True)
    color         = db.Column(db.String(50),  nullable=True)
    care          = db.Column(db.String(200), nullable=True)
    in_stock      = db.Column(db.Boolean, default=True)
    is_new        = db.Column(db.Boolean, default=False)
    is_active     = db.Column(db.Boolean, default=True)
    created_at    = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at    = db.Column(db.DateTime,
                              default=lambda: datetime.now(timezone.utc),
                              onupdate=lambda: datetime.now(timezone.utc))

    # ── Relationships ─────────────────────────────────────
    order_items = db.relationship("OrderItem", back_populates="product", lazy="dynamic")

    # ── Computed ──────────────────────────────────────────
    @property
    def discount_amount(self):
        if self.original_price and self.price:
            return float(self.original_price) - float(self.price)
        return 0

    def to_dict(self) -> dict:
        return {
            "id":             self.id,
            "name":           self.name,
            "description":    self.description,
            "price":          float(self.price),
            "original_price": float(self.original_price) if self.original_price else None,
            "discount":       self.discount,
            "discount_amount": self.discount_amount,
            "image_url":      self.image_url,
            "occasion":       self.occasion,
            "fabric":         self.fabric,
            "color":          self.color,
            "care":           self.care,
            "in_stock":       self.in_stock,
            "is_new":         self.is_new,
            "is_active":      self.is_active,
            "created_at":     self.created_at.isoformat() if self.created_at else None,
            "updated_at":     self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        return f"<Product {self.name}>"
