import logging
import traceback
import sys
from flask import request, jsonify, current_app
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    get_jwt_identity, jwt_required
)
from flask_mail import Message
from flask_bcrypt import Bcrypt
from sqlalchemy.exc import IntegrityError, OperationalError
from app import db, mail
from app.models.user import User
from app.models.email_verification import EmailVerification
from app.utils.helpers import success_response, error_response, validate_required

bcrypt = Bcrypt()

# ── Configure logging ──────────────────────────────────────────────────────────
logger = logging.getLogger(__name__)


def register():
    """
    Register new user with email verification via OTP.
    
    Flow:
    1. Validate input
    2. Check for duplicate email/username
    3. Hash password
    4. Create email verification record
    5. Send OTP email
    6. Return success or detailed error
    """
    try:
        # ────────────────────────────────────────────────────────────────────────
        # STEP 1: Parse and validate request
        # ────────────────────────────────────────────────────────────────────────
        logger.info("📝 Signup request received")
        
        data = request.get_json(silent=True) or {}
        logger.debug(f"Request data: username={data.get('username')}, email={data.get('email')}")

        # Validate required fields
        missing = validate_required(data, ["username", "email", "password"])
        if missing:
            logger.warning(f"❌ Missing required fields: {missing}")
            return error_response(f"Missing required fields: {', '.join(missing)}", 400)

        # Sanitize input
        username = data.get("username", "").strip()
        email = data.get("email", "").strip().lower()
        password = data.get("password", "").strip()
        phone = data.get("phone", "").strip()

        # Validate input format
        if not username or len(username) < 3:
            logger.warning(f"❌ Invalid username length: {len(username)}")
            return error_response("Username must be at least 3 characters long", 400)

        if not email or "@" not in email:
            logger.warning(f"❌ Invalid email format: {email}")
            return error_response("Invalid email address", 400)

        if not password or len(password) < 6:
            logger.warning(f"❌ Invalid password length: {len(password)}")
            return error_response("Password must be at least 6 characters long", 400)

        logger.info(f"✅ Input validation passed for email={email}, username={username}")

        # ────────────────────────────────────────────────────────────────────────
        # STEP 2: Check database connection
        # ────────────────────────────────────────────────────────────────────────
        try:
            logger.info("🔗 Testing database connection...")
            db.session.execute(db.text("SELECT 1"))
            logger.info("✅ Database connection OK")
        except OperationalError as db_err:
            logger.error(f"❌ DATABASE CONNECTION ERROR: {str(db_err)}")
            logger.error(f"Traceback:\n{traceback.format_exc()}")
            return error_response("Database connection failed. Please try again later.", 503)
        except Exception as db_err:
            logger.error(f"❌ DATABASE ERROR (unexpected): {str(db_err)}")
            logger.error(f"Traceback:\n{traceback.format_exc()}")
            return error_response("Database error. Please try again later.", 503)

        # ────────────────────────────────────────────────────────────────────────
        # STEP 3: Check for duplicate email
        # ────────────────────────────────────────────────────────────────────────
        logger.info(f"🔍 Checking for duplicate email: {email}")
        try:
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                logger.warning(f"❌ Email already registered: {email}")
                return error_response("This email is already registered. Please login or use a different email.", 409)
            logger.info(f"✅ Email is available: {email}")
        except Exception as query_err:
            logger.error(f"❌ ERROR checking email: {str(query_err)}")
            logger.error(f"Traceback:\n{traceback.format_exc()}")
            return error_response("Could not verify email. Please try again.", 500)

        # ────────────────────────────────────────────────────────────────────────
        # STEP 4: Check for duplicate username
        # ────────────────────────────────────────────────────────────────────────
        logger.info(f"🔍 Checking for duplicate username: {username}")
        try:
            existing_username = User.query.filter_by(username=username).first()
            if existing_username:
                logger.warning(f"❌ Username already taken: {username}")
                return error_response("This username is already taken. Please choose a different one.", 409)
            logger.info(f"✅ Username is available: {username}")
        except Exception as query_err:
            logger.error(f"❌ ERROR checking username: {str(query_err)}")
            logger.error(f"Traceback:\n{traceback.format_exc()}")
            return error_response("Could not verify username. Please try again.", 500)

        # ────────────────────────────────────────────────────────────────────────
        # STEP 5: Hash password
        # ────────────────────────────────────────────────────────────────────────
        logger.info("🔐 Hashing password...")
        try:
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
            logger.info("✅ Password hashed successfully")
        except Exception as hash_err:
            logger.error(f"❌ PASSWORD HASHING ERROR: {str(hash_err)}")
            logger.error(f"Traceback:\n{traceback.format_exc()}")
            return error_response("Failed to process password. Please try again.", 500)

        # ────────────────────────────────────────────────────────────────────────
        # STEP 6: Create email verification record
        # ────────────────────────────────────────────────────────────────────────
        logger.info(f"📧 Creating email verification for {email}")
        try:
            otp = EmailVerification.create_verification(
                email=email,
                username=username,
                password=hashed_password,
                phone=phone
            )
            logger.info(f"✅ Email verification created. OTP={otp}")
        except IntegrityError as integrity_err:
            logger.error(f"❌ DATABASE INTEGRITY ERROR: {str(integrity_err)}")
            logger.error(f"Traceback:\n{traceback.format_exc()}")
            db.session.rollback()
            # Could be a race condition (email just registered by another request)
            return error_response("Email verification failed. This email might already be registered.", 409)
        except Exception as verify_err:
            logger.error(f"❌ EMAIL VERIFICATION ERROR: {str(verify_err)}")
            logger.error(f"Traceback:\n{traceback.format_exc()}")
            db.session.rollback()
            return error_response("Failed to create verification. Please try again.", 500)

        # ────────────────────────────────────────────────────────────────────────
        # STEP 7: Send OTP email
        # ────────────────────────────────────────────────────────────────────────
        logger.info(f"📬 Sending OTP email to {email}")
        try:
            # Check Mail configuration first
            if not current_app.config.get('MAIL_SERVER'):
                logger.error("❌ MAIL_SERVER not configured")
                # Delete the verification record since we can't send email
                EmailVerification.query.filter_by(email=email).delete()
                db.session.commit()
                return error_response("Email service is not configured. Please contact support.", 503)

            logger.debug(f"Mail server: {current_app.config.get('MAIL_SERVER')}")
            logger.debug(f"Mail port: {current_app.config.get('MAIL_PORT')}")
            logger.debug(f"Mail TLS: {current_app.config.get('MAIL_USE_TLS')}")

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
                html=html_body,
                sender=current_app.config.get('MAIL_DEFAULT_SENDER')
            )
            mail.send(msg)
            logger.info(f"✅ OTP email sent successfully to {email}")

        except Exception as mail_err:
            logger.error(f"❌ EMAIL SENDING ERROR for {email}: {str(mail_err)}")
            logger.error(f"Exception type: {type(mail_err).__name__}")
            logger.error(f"Traceback:\n{traceback.format_exc()}")
            
            # Clean up the verification record since we couldn't send email
            try:
                EmailVerification.query.filter_by(email=email).delete()
                db.session.commit()
                logger.info(f"🧹 Cleaned up verification record for {email}")
            except Exception as cleanup_err:
                logger.error(f"❌ Cleanup error: {str(cleanup_err)}")
                db.session.rollback()
            
            # Check if it's a SMTP authentication error
            if "SMTP" in str(mail_err) or "Authentication" in str(mail_err):
                return error_response("Email service authentication failed. Please contact support.", 503)
            
            return error_response("Failed to send verification email. Please try again later.", 500)

        # ────────────────────────────────────────────────────────────────────────
        # SUCCESS: Return response
        # ────────────────────────────────────────────────────────────────────────
        logger.info(f"✅ SIGNUP SUCCESSFUL for {email}")
        return success_response(
            data={"email": email},
            message="Verification OTP sent to your email. Please check your inbox and spam folder.",
            status_code=200,
        )

    except Exception as unexpected_err:
        # Catch any unexpected errors
        logger.critical(f"❌ UNEXPECTED ERROR in register(): {str(unexpected_err)}")
        logger.critical(f"Exception type: {type(unexpected_err).__name__}")
        logger.critical(f"Full traceback:\n{traceback.format_exc()}")
        
        # Try to rollback any pending transactions
        try:
            db.session.rollback()
        except:
            pass
        
        # Return safe error message to user (don't expose internal details)
        return error_response("An unexpected error occurred during signup. Please try again later.", 500)


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
