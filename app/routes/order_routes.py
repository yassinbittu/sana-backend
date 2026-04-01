from flask import Blueprint
from app.controllers import order_controller
from app.middleware.auth_middleware import jwt_required_custom, admin_required

order_bp = Blueprint("orders", __name__)


@order_bp.post("")
def create_order():
    """
    Create order
    ---
    tags:
      - Orders
    """
    return order_controller.create_order()


@order_bp.get("/track/<string:order_number>")
def track(order_number):
    """
    Track order by order number
    ---
    tags:
      - Orders
    """
    return order_controller.get_order_by_number(order_number)


@order_bp.get("/my")
@jwt_required_custom
def my_orders():
    """
    Get my orders
    ---
    tags:
      - Orders
    """
    return order_controller.get_my_orders()


@order_bp.get("")
@admin_required
def all_orders():
    """
    Admin get all orders
    ---
    tags:
      - Orders
    """
    return order_controller.admin_get_all_orders()


@order_bp.patch("/<int:order_id>/status")
@admin_required
def update_status(order_id):
    """
    Update order status
    ---
    tags:
      - Orders
    """
    return order_controller.admin_update_order_status(order_id)


@order_bp.delete("/<int:order_id>")
@admin_required
def delete_order(order_id):
    """
    Delete order
    ---
    tags:
      - Orders
    """
    return order_controller.admin_delete_order(order_id)