from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from app.models.user import User


def jwt_required_custom(fn):
    """Require a valid JWT. Attach current_user to g."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))  # Convert string back to int
        if not user or not user.is_active:
            return jsonify({"success": False, "message": "User not found or inactive"}), 401
        return fn(*args, **kwargs)
    return wrapper


def admin_required(fn):
    """Require a valid JWT AND admin role."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))  # Convert string back to int
        if not user or not user.is_active:
            return jsonify({"success": False, "message": "User not found or inactive"}), 401
        if not user.is_admin():
            return jsonify({"success": False, "message": "Admin access required"}), 403
        return fn(*args, **kwargs)
    return wrapper


def get_current_user() -> User | None:
    """Safely return the current logged-in User or None."""
    try:
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        return User.query.get(user_id)
    except Exception:
        return None
