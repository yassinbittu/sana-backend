from app import db
from datetime import datetime, timedelta
import random
import string


class EmailVerification(db.Model):
    __tablename__ = "email_verifications"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    otp = db.Column(db.String(6), nullable=False)
    username = db.Column(db.String(80), nullable=True)
    password = db.Column(db.String(256), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    expires_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @staticmethod
    def generate_otp():
        return ''.join(random.choices(string.digits, k=6))

    @classmethod
    def create_verification(cls, email, username=None, password=None, phone=None):
        # Delete any existing verification for this email
        cls.query.filter_by(email=email).delete()
        otp = cls.generate_otp()
        expires_at = datetime.utcnow() + timedelta(minutes=10)  # OTP valid for 10 minutes
        verification = cls(
            email=email, 
            otp=otp, 
            expires_at=expires_at,
            username=username,
            password=password,
            phone=phone
        )
        db.session.add(verification)
        db.session.commit()
        return otp

    @classmethod
    def verify_otp(cls, email, otp):
        verification = cls.query.filter_by(email=email, otp=otp).first()
        if verification and verification.expires_at > datetime.utcnow():
            return verification
        return False