from datetime import datetime, timezone
from app import db, bcrypt


class User(db.Model):
    __tablename__ = "users"

    id         = db.Column(db.Integer, primary_key=True)
    username   = db.Column(db.String(80),  unique=True, nullable=False)
    email      = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    phone      = db.Column(db.String(15),  nullable=True)
    role       = db.Column(db.String(20),  nullable=False, default="customer")
    is_active  = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime,
                           default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    # ── Relationships ─────────────────────────────────────
    orders = db.relationship("Order", back_populates="user", lazy="dynamic")

    # ── Password ──────────────────────────────────────────
    def set_password(self, password: str):
        self.password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    def check_password(self, password: str) -> bool:
        return bcrypt.check_password_hash(self.password_hash, password)

    # ── Helpers ───────────────────────────────────────────
    def is_admin(self) -> bool:
        return self.role == "admin"

    def to_dict(self, include_private=False) -> dict:
        data = {
            "id":         self.id,
            "username":   self.username,
            "email":      self.email,
            "phone":      self.phone,
            "role":       self.role,
            "is_active":  self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
        return data

    def __repr__(self):
        return f"<User {self.username} [{self.role}]>"
