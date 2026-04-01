from flask import Blueprint
from app.controllers import admin_controller, product_controller, order_controller
from app.middleware.auth_middleware import admin_required

admin_bp = Blueprint("admin", __name__)
admin_bp.before_request(admin_required)


@admin_bp.get("/dashboard")
def dashboard():
    """
    Admin dashboard
    ---
    tags:
      - Admin
    """
    return admin_controller.get_dashboard_stats()


@admin_bp.get("/users")
def users():
    """
    Get all users
    ---
    tags:
      - Admin
    """
    return admin_controller.get_all_users()


@admin_bp.get("/users/<int:user_id>")
def user(user_id):
    """
    Get user by ID
    ---
    tags:
      - Admin
    """
    return admin_controller.get_user(user_id)


@admin_bp.patch("/users/<int:user_id>/toggle")
def toggle(user_id):
    """
    Toggle user status
    ---
    tags:
      - Admin
    """
    return admin_controller.toggle_user_status(user_id)


@admin_bp.delete("/users/<int:user_id>")
def delete_user(user_id):
    """
    Delete user
    ---
    tags:
      - Admin
    """
    return admin_controller.delete_user(user_id)


@admin_bp.get("/products")
def all_products():
    """
    Admin get all products
    ---
    tags:
      - Admin
    """
    return product_controller.get_all_products()


@admin_bp.get("/orders")
def all_orders():
    """
    Admin get all orders
    ---
    tags:
      - Admin
    """
    return order_controller.admin_get_all_orders()