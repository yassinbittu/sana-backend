from flask import request, jsonify
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    get_jwt_identity, jwt_required
)
from flask_mail import Message
from app import db, mail
from app.models.user import User
from app.models.email_verification import EmailVerification
from app.utils.helpers import success_response, error_response, validate_required


def register():
    data = request.get_json(silent=True) or {}

    # ── Validate required fields ──────────────────────────
    missing = validate_required(data, ["username", "email", "password"])
    if missing:
        return error_response(f"Missing fields: {', '.join(missing)}")

    username = data["username"].strip()
    email    = data["email"].strip().lower()
    password = data["password"]

    if len(password) < 6:
        return error_response("Password must be at least 6 characters")

    if User.query.filter_by(email=email).first():
        return error_response("Email is already registered", 409)

    if User.query.filter_by(username=username).first():
        return error_response("Username is already taken", 409)

    # ── Create email verification ─────────────────────────
    otp = EmailVerification.create_verification(email)

    # ── Send OTP email ────────────────────────────────────
    try:
        msg = Message(
            subject="SANA - Email Verification",
            recipients=[email],
            body=f"Your OTP for email verification is: {otp}\n\nThis OTP will expire in 10 minutes."
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


def admin_login():
    data = request.get_json(silent=True) or {}

    missing = validate_required(data, ["email", "password"])
    if missing:
        return error_response(f"Missing fields: {', '.join(missing)}")

    user = User.query.filter_by(email=data["email"]).first()
    if not user or not user.check_password(data["password"]) or not user.is_admin():
        return error_response("Invalid admin credentials", 401)

    access_token  = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))

    return success_response(
        data={
            "user":          user.to_dict(),
            "access_token":  access_token,
            "refresh_token": refresh_token,
        },
        message="Admin login successful",
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

    missing = validate_required(data, ["email", "otp", "username", "password"])
    if missing:
        return error_response(f"Missing fields: {', '.join(missing)}")

    email = data["email"].strip().lower()
    otp = data["otp"].strip()
    username = data["username"].strip()
    password = data["password"]

    # ── Verify OTP ────────────────────────────────────────
    if not EmailVerification.verify_otp(email, otp):
        return error_response("Invalid or expired OTP", 400)

    # ── Check if user already exists (in case of retry) ───
    if User.query.filter_by(email=email).first():
        return error_response("Email is already registered", 409)

    if User.query.filter_by(username=username).first():
        return error_response("Username is already taken", 409)

    # ── Create user ───────────────────────────────────────
    user = User(
        username=username,
        email=email,
        phone=data.get("phone"),
        role="customer",
    )
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    access_token  = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)

    return success_response(
        data={
            "user":          user.to_dict(),
            "access_token":  access_token,
            "refresh_token": refresh_token,
        },
        message="Account verified and created successfully",
        status_code=201,
    )
