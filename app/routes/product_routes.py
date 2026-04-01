from flask import Blueprint
from app.controllers import product_controller
from app.middleware.auth_middleware import admin_required

product_bp = Blueprint("products", __name__)


@product_bp.get("")
def get_products():
    """
    Get all products
    ---
    tags:
      - Products
    """
    return product_controller.get_all_products()


@product_bp.get("/filters")
def get_filters():
    """
    Get product filters
    ---
    tags:
      - Products
    """
    return product_controller.get_product_filters()


@product_bp.get("/<int:product_id>")
def get_product(product_id):
    """
    Get product by ID
    ---
    tags:
      - Products
    """
    return product_controller.get_product(product_id)


@product_bp.post("")
@admin_required
def create_product():
    """
    Create product (Admin)
    ---
    tags:
      - Products
    """
    return product_controller.create_product()


@product_bp.put("/<int:product_id>")
@admin_required
def update_product(product_id):
    """
    Update product
    ---
    tags:
      - Products
    """
    return product_controller.update_product(product_id)


@product_bp.delete("/<int:product_id>")
@admin_required
def delete_product(product_id):
    """
    Delete product
    ---
    tags:
      - Products
    """
    return product_controller.delete_product(product_id)