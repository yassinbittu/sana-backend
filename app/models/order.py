from datetime import datetime, timezone
from app import db


class Order(db.Model):
    __tablename__ = "orders"

    # ── Status choices ────────────────────────────────────
    STATUS_PENDING    = "pending"
    STATUS_CONFIRMED  = "confirmed"
    STATUS_PROCESSING = "processing"
    STATUS_SHIPPED    = "shipped"
    STATUS_DELIVERED  = "delivered"
    STATUS_CANCELLED  = "cancelled"

    VALID_STATUSES = [
        STATUS_PENDING, STATUS_CONFIRMED, STATUS_PROCESSING,
        STATUS_SHIPPED, STATUS_DELIVERED, STATUS_CANCELLED,
    ]

    id               = db.Column(db.Integer, primary_key=True)
    order_number     = db.Column(db.String(20), unique=True, nullable=False)
    user_id          = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    # Customer info (for guest / WhatsApp orders)
    customer_name    = db.Column(db.String(100), nullable=False)
    customer_phone   = db.Column(db.String(15),  nullable=False)
    customer_email   = db.Column(db.String(120), nullable=True)
    customer_address = db.Column(db.Text,         nullable=True)

    # Order details
    total_amount     = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    status           = db.Column(db.String(20), nullable=False, default=STATUS_PENDING)
    notes            = db.Column(db.Text,   nullable=True)
    source           = db.Column(db.String(20), default="website")  # website | whatsapp

    # WhatsApp notification tracking
    wa_notified      = db.Column(db.Boolean, default=False)
    wa_message_id    = db.Column(db.String(100), nullable=True)

    created_at       = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at       = db.Column(db.DateTime,
                                 default=lambda: datetime.now(timezone.utc),
                                 onupdate=lambda: datetime.now(timezone.utc))

    # ── Relationships ─────────────────────────────────────
    user   = db.relationship("User", back_populates="orders")
    items  = db.relationship("OrderItem", back_populates="order",
                             cascade="all, delete-orphan", lazy="select")

    # ── Helpers ───────────────────────────────────────────
    def calculate_total(self):
        self.total_amount = sum(item.subtotal for item in self.items)

    def to_dict(self, include_items=True) -> dict:
        data = {
            "id":               self.id,
            "order_number":     self.order_number,
            "user_id":          self.user_id,
            "customer_name":    self.customer_name,
            "customer_phone":   self.customer_phone,
            "customer_email":   self.customer_email,
            "customer_address": self.customer_address,
            "total_amount":     float(self.total_amount),
            "status":           self.status,
            "notes":            self.notes,
            "source":           self.source,
            "wa_notified":      self.wa_notified,
            "created_at":       self.created_at.isoformat() if self.created_at else None,
            "updated_at":       self.updated_at.isoformat() if self.updated_at else None,
        }
        if include_items:
            data["items"] = [item.to_dict() for item in self.items]
        return data

    def __repr__(self):
        return f"<Order #{self.order_number} [{self.status}]>"


class OrderItem(db.Model):
    __tablename__ = "order_items"

    id         = db.Column(db.Integer, primary_key=True)
    order_id   = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=True)

    # Snapshot at time of order (in case product is edited later)
    product_name  = db.Column(db.String(200), nullable=False)
    product_image = db.Column(db.String(500), nullable=True)
    unit_price    = db.Column(db.Numeric(10, 2), nullable=False)
    quantity      = db.Column(db.Integer, nullable=False, default=1)

    # ── Relationships ─────────────────────────────────────
    order   = db.relationship("Order", back_populates="items")
    product = db.relationship("Product", back_populates="order_items")

    @property
    def subtotal(self):
        return float(self.unit_price) * self.quantity

    def to_dict(self) -> dict:
        return {
            "id":            self.id,
            "product_id":    self.product_id,
            "product_name":  self.product_name,
            "product_image": self.product_image,
            "unit_price":    float(self.unit_price),
            "quantity":      self.quantity,
            "subtotal":      self.subtotal,
        }

    def __repr__(self):
        return f"<OrderItem {self.product_name} x{self.quantity}>"
