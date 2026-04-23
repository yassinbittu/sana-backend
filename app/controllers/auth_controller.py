from flask import request, jsonify
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    get_jwt_identity, jwt_required
)
from flask_mail import Message
from flask_bcrypt import Bcrypt
from app import db, mail
from app.models.user import User
from app.models.email_verification import EmailVerification
from app.utils.helpers import success_response, error_response, validate_required

bcrypt = Bcrypt()


def register():
    data = request.get_json(silent=True) or {}

    # ── Validate required fields ──────────────────────────
    missing = validate_required(data, ["username", "email", "password"])
    if missing:
        return error_response(f"Missing fields: {', '.join(missing)}")

    username = data["username"].strip()
    email    = data["email"].strip().lower()
    password = data["password"]
    phone    = data.get("phone", "")

    if len(password) < 6:
        return error_response("Password must be at least 6 characters")

    if User.query.filter_by(email=email).first():
        return error_response("Email is already registered", 409)

    if User.query.filter_by(username=username).first():
        return error_response("Username is already taken", 409)

    # ── Hash password and create email verification ───────
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    otp = EmailVerification.create_verification(email, username, hashed_password, phone)

    # ── Send OTP email ────────────────────────────────────
    try:
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>SANA Sarees - Email Verification</title>
        </head>
        <body style="margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f5f5f5;">
            <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #f5f5f5; padding: 20px;">
                <tr>
                    <td align="center">
                        <table width="600" cellpadding="0" cellspacing="0" style="background-color: #ffffff; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                            <!-- Header -->
                            <tr>
                                <td style="background: linear-gradient(135deg, #d4a574 0%, #8b5a2b 100%); padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                                    <h1 style="color: #ffffff; margin: 0; font-size: 32px; font-weight: bold;">SANA Sarees</h1>
                                    <p style="color: #ffffff; margin: 5px 0 0 0; font-size: 14px; opacity: 0.9;">Elegant Traditional Wear</p>
                                </td>
                            </tr>
                            <!-- Content -->
                            <tr>
                                <td style="padding: 40px 30px;">
                                    <h2 style="color: #333333; margin: 0 0 20px 0; font-size: 24px;">Welcome to SANA Sarees! 🎉</h2>
                                    <p style="color: #666666; margin: 0 0 20px 0; font-size: 16px; line-height: 1.6;">
                                        Thank you for joining our family. We're excited to have you on board!
                                    </p>
                                    <p style="color: #666666; margin: 0 0 30px 0; font-size: 16px; line-height: 1.6;">
                                        Your One-Time Password (OTP) for email verification is:
                                    </p>
                                    <!-- OTP Box -->
                                    <table width="100%" cellpadding="0" cellspacing="0">
                                        <tr>
                                            <td align="center">
                                                <div style="background: linear-gradient(135deg, #f8f4f0 0%, #efe6dc 100%); border: 2px dashed #d4a574; border-radius: 10px; padding: 20px 40px; display: inline-block;">
                                                    <span style="font-size: 36px; font-weight: bold; color: #8b5a2b; letter-spacing: 8px;">{otp}</span>
                                                </div>
                                            </td>
                                        </tr>
                                    </table>
                                    <p style="color: #999999; margin: 30px 0 0 0; font-size: 14px; text-align: center;">
                                        ⏱️ This OTP will expire in <strong>10 minutes</strong>
                                    </p>
                                    <p style="color: #999999; margin: 20px 0 0 0; font-size: 12px; text-align: center;">
                                        If you didn't request this, please ignore this email.
                                    </p>
                                </td>
                            </tr>
                            <!-- Footer -->
                            <tr>
                                <td style="background-color: #333333; padding: 20px 30px; border-radius: 0 0 10px 10px;">
                                    <table width="100%" cellpadding="0" cellspacing="0">
                                        <tr>
                                            <td align="center">
                                                <p style="color: #ffffff; margin: 0 0 10px 0; font-size: 14px;">Happy Shopping! 🛍️</p>
                                                <p style="color: #888888; margin: 0; font-size: 12px;">
                                                    © 2026 SANA Sarees. All rights reserved.
                                                </p>
                                            </td>
                                        </tr>
                                    </table>
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>
            </table>
        </body>
        </html>
        """
        msg = Message(
            subject="SANA Sarees - Email Verification",
            recipients=[email],
            html=html_body
        )
        mail.send(msg)
    except Exception as e:
        print(f"[EMAIL ERROR] Failed to send OTP to {email}: {str(e)}")
        return error_response("Failed to send verification email. Please try again.", 500)

    return success_response(
        data={"email": email},
        message="Verification OTP sent to your email. Please check your inbox.",
        status_code=200,
    )


def login():
    data = request.get_json(silent=True) or {}

    missing = validate_required(data, ["email", "password"])
    if missing:
        return error_response(f"Missing fields: {', '.join(missing)}")

    email    = data["email"].strip().lower()
    password = data["password"]

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return error_response("Invalid email or password", 401)

    if not user.is_active:
        return error_response("Account is deactivated. Please contact support.", 403)

    access_token  = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))

    return success_response(
        data={
            "user":          user.to_dict(),
            "access_token":  access_token,
            "refresh_token": refresh_token,
        },
        message="Login successful",
    )


@jwt_required(refresh=True)
def refresh_token():
    user_id = get_jwt_identity()
    user    = User.query.get(int(user_id))  # Convert string back to int
    if not user or not user.is_active:
        return error_response("User not found", 401)

    new_access = create_access_token(identity=str(user.id))
    return success_response(
        data={"access_token": new_access},
        message="Token refreshed",
    )


@jwt_required()
def get_profile():
    user_id = get_jwt_identity()
    user    = User.query.get(int(user_id))  # Convert string back to int
    if not user:
        return error_response("User not found", 404)
    return success_response(data={"user": user.to_dict()})


@jwt_required()
def update_profile():
    user_id = get_jwt_identity()
    user    = User.query.get(user_id)
    if not user:
        return error_response("User not found", 404)

    data = request.get_json(silent=True) or {}

    if "username" in data:
        new_username = data["username"].strip()
        existing = User.query.filter_by(username=new_username).first()
        if existing and existing.id != user.id:
            return error_response("Username is already taken", 409)
        user.username = new_username

    if "phone" in data:
        user.phone = data["phone"]

    if "password" in data:
        if len(data["password"]) < 6:
            return error_response("Password must be at least 6 characters")
        user.set_password(data["password"])

    db.session.commit()
    return success_response(data={"user": user.to_dict()}, message="Profile updated")


def verify_otp():
    data = request.get_json(silent=True) or {}

    missing = validate_required(data, ["email", "otp"])
    if missing:
        return error_response(f"Missing fields: {', '.join(missing)}")

    email = data["email"].strip().lower()
    otp = data["otp"].strip()

    # ── Verify OTP and get verification record ────────────
    verification = EmailVerification.verify_otp(email, otp)
    if not verification:
        return error_response("Invalid or expired OTP", 400)

    # ── Check if user already exists ───────────────────────
    if User.query.filter_by(email=email).first():
        return error_response("Email is already registered", 409)

    # ── Get stored username and password ───────────────────
    username = verification.username
    password = verification.password

    if not username or not password:
        return error_response("Registration data not found. Please register again.", 400)

    if User.query.filter_by(username=username).first():
        return error_response("Username is already taken", 409)

    # ── Create user ───────────────────────────────────────
    user = User(
        username=username,
        email=email,
        phone=verification.phone,
        role="customer",
    )
    user.set_password(password)
    db.session.add(user)
    
    # Delete verification record
    db.session.delete(verification)
    db.session.commit()

    access_token  = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))

    return success_response(
        data={
            "user":          user.to_dict(),
            "access_token":  access_token,
            "refresh_token": refresh_token,
        },
        message="Account verified and created successfully",
        status_code=201,
    )
