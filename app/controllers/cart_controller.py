from flask import request
from app import db
from app.models.cart import Cart
from app.models.product import Product
from app.utils.helpers import success_response, error_response

GUEST_CART_USER_ID = None


def get_cart():
    """Get all items in guest cart"""
    cart_items = Cart.query.filter_by(user_id=GUEST_CART_USER_ID).all()

    # Calculate totals
    subtotal = sum(item.subtotal for item in cart_items)
    discount_total = sum(item.discount_amount for item in cart_items)
    total = subtotal - discount_total

    return success_response(data={
        "items": [item.to_dict() for item in cart_items],
        "summary": {
            "item_count": len(cart_items),
            "subtotal": subtotal,
            "discount_total": discount_total,
            "total": total
        }
    })


def add_to_cart():
    """Add product to cart"""
    data = request.get_json(silent=True) or {}

    # Validate required fields
    if "product_id" not in data:
        return error_response("product_id is required")

    if "quantity" not in data:
        data["quantity"] = 1

    try:
        product_id = int(data["product_id"])
        quantity = int(data["quantity"])
    except (ValueError, TypeError):
        return error_response("product_id and quantity must be valid numbers")

    if quantity <= 0:
        return error_response("Quantity must be greater than 0")

    # Check if product exists and is active
    product = Product.query.filter_by(id=product_id, is_active=True).first()
    if not product:
        return error_response("Product not found", 404)

    if not product.in_stock:
        return error_response("Product is out of stock")

    # Check if item already in cart
    existing_item = Cart.query.filter_by(
        user_id=GUEST_CART_USER_ID,
        product_id=product_id
    ).first()

    if existing_item:
        # Update quantity
        existing_item.quantity += quantity
        db.session.commit()
        return success_response(
            data={"cart_item": existing_item.to_dict()},
            message="Cart updated successfully"
        )
    else:
        # Create new cart item
        cart_item = Cart(
            user_id=GUEST_CART_USER_ID,
            product_id=product_id,
            quantity=quantity
        )
        db.session.add(cart_item)
        db.session.commit()
        return success_response(
            data={"cart_item": cart_item.to_dict()},
            message="Product added to cart successfully",
            status_code=201
        )


def update_cart_item(cart_item_id):
    """Update cart item quantity"""
    data = request.get_json(silent=True) or {}

    if "quantity" not in data:
        return error_response("quantity is required")

    try:
        quantity = int(data["quantity"])
    except (ValueError, TypeError):
        return error_response("quantity must be a valid number")

    if quantity <= 0:
        return error_response("Quantity must be greater than 0")

    # Find cart item
    cart_item = Cart.query.filter_by(
        id=cart_item_id,
        user_id=GUEST_CART_USER_ID
    ).first()
    if not cart_item:
        return error_response("Cart item not found", 404)

    # Check if product is still available
    if not cart_item.product.in_stock:
        return error_response("Product is no longer available")

    # Update quantity
    cart_item.quantity = quantity
    db.session.commit()

    return success_response(
        data={"cart_item": cart_item.to_dict()},
        message="Cart item updated successfully"
    )


def remove_from_cart(cart_item_id):
    """Remove item from cart"""
    cart_item = Cart.query.filter_by(
        id=cart_item_id,
        user_id=GUEST_CART_USER_ID
    ).first()
    if not cart_item:
        return error_response("Cart item not found", 404)

    db.session.delete(cart_item)
    db.session.commit()

    return success_response(message="Item removed from cart successfully")


def clear_cart():
    """Remove all items from guest cart"""
    Cart.query.filter_by(user_id=GUEST_CART_USER_ID).delete()
    db.session.commit()

    return success_response(message="Cart cleared successfully")


def get_cart_count():
    """Get total number of items in cart"""
    count = Cart.query.filter_by(user_id=GUEST_CART_USER_ID).count()

    return success_response(data={"count": count})
