from flask import Blueprint
from app.controllers import auth_controller

auth_bp = Blueprint("auth", __name__)


@auth_bp.post("/register")
def register():
    """
    Register new user
    ---
    tags:
      - Auth
    """
    return auth_controller.register()


@auth_bp.post("/login")
def login():
    """
    Login user
    ---
    tags:
      - Auth
    """
    return auth_controller.login()


@auth_bp.post("/admin/login")
def admin_login():
    """
    Admin login
    ---
    tags:
      - Auth
    """
    return auth_controller.admin_login()


@auth_bp.post("/refresh")
def refresh():
    """
    Refresh JWT token
    ---
    tags:
      - Auth
    """
    return auth_controller.refresh_token()


@auth_bp.get("/me")
def profile():
    """
    Get user profile
    ---
    tags:
      - Auth
    """
    return auth_controller.get_profile()


@auth_bp.patch("/me")
def update_profile():
    """
    Update user profile
    ---
    tags:
      - Auth
    """
    return auth_controller.update_profile()