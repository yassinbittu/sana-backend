from datetime import datetime, timezone
from app import db


class Cart(db.Model):
    __tablename__ = "carts"

    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    quantity   = db.Column(db.Integer, nullable=False, default=1)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime,
                           default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    # ── Relationships ─────────────────────────────────────
    user    = db.relationship("User", backref="cart_items")
    product = db.relationship("Product", backref="cart_items")

    # ── Computed ──────────────────────────────────────────
    @property
    def subtotal(self):
        """Calculate subtotal for this cart item"""
        return float(self.product.price) * self.quantity

    @property
    def discount_amount(self):
        """Calculate discount amount for this cart item"""
        if self.product.discount:
            return self.subtotal * (self.product.discount / 100)
        return 0

    @property
    def total(self):
        """Calculate total after discount for this cart item"""
        return self.subtotal - self.discount_amount

    def to_dict(self) -> dict:
        return {
            "id":             self.id,
            "user_id":        self.user_id,
            "product":        self.product.to_dict() if self.product else None,
            "quantity":       self.quantity,
            "subtotal":       self.subtotal,
            "discount_amount": self.discount_amount,
            "total":          self.total,
            "created_at":     self.created_at.isoformat() if self.created_at else None,
            "updated_at":     self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        return f"<Cart {self.user_id}:{self.product_id} x{self.quantity}>"