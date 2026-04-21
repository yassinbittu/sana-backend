from sqlalchemy.exc import OperationalError, ProgrammingError

from app import db
from app.models.user import User


def ensure_admin_user(app):
    """Create or repair the configured admin user if it is missing."""
    admin_email = (app.config.get("ADMIN_EMAIL") or "").strip().lower()
    admin_username = (app.config.get("ADMIN_USERNAME") or "admin").strip()
    admin_password = app.config.get("ADMIN_PASSWORD") or ""

    if not admin_email or not admin_password:
        app.logger.warning("Admin bootstrap skipped because admin credentials are incomplete.")
        return

    try:
        admin = User.query.filter_by(email=admin_email).first()

        if admin:
            changed = False
            if admin.role != "admin":
                admin.role = "admin"
                changed = True
            if not admin.is_active:
                admin.is_active = True
                changed = True
            if admin.username != admin_username:
                admin.username = admin_username
                changed = True
            if not admin.check_password(admin_password):
                admin.set_password(admin_password)
                changed = True

            if changed:
                db.session.commit()
                app.logger.info("Configured admin user was updated successfully.")
            return

        existing_admin = User.query.filter_by(role="admin").first()
        if existing_admin:
            existing_admin.email = admin_email
            existing_admin.username = admin_username
            existing_admin.is_active = True
            if not existing_admin.check_password(admin_password):
                existing_admin.set_password(admin_password)
            db.session.commit()
            app.logger.info("Existing admin user was aligned with configured credentials.")
            return

        admin = User(
            username=admin_username,
            email=admin_email,
            role="admin",
            is_active=True,
        )
        admin.set_password(admin_password)
        db.session.add(admin)
        db.session.commit()
        app.logger.info("Configured admin user was created successfully.")
    except (OperationalError, ProgrammingError) as exc:
        db.session.rollback()
        app.logger.warning("Admin bootstrap skipped because the database is not ready: %s", exc)
