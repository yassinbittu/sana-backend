from flask import request
from flask_jwt_extended import get_jwt_identity
from app import db
from app.models.order import Order, OrderItem
from app.models.product import Product
from app.utils.helpers import (
    success_response, error_response, paginated_response,
    validate_required, generate_order_number, validate_phone
)
from app.utils.whatsapp import WhatsAppService


def create_order():
    """
    Create an order from the website.
    Accepts a list of items with product_id + quantity.
    Automatically notifies the admin via WhatsApp.
    """
    data = request.get_json(silent=True) or {}

    missing = validate_required(data, ["customer_name", "customer_phone", "items"])
    if missing:
        return error_response(f"Missing required fields: {', '.join(missing)}")

    if not validate_phone(data["customer_phone"]):
        return error_response("Invalid phone number")

    items_data = data.get("items", [])
    if not items_data or not isinstance(items_data, list):
        return error_response("Order must contain at least one item")

    # ── Resolve user (optional) ───────────────────────────
    user_id = None
    try:
        from flask_jwt_extended import verify_jwt_in_request
        verify_jwt_in_request(optional=True)
        user_id = get_jwt_identity()
    except Exception:
        pass

    # ── Build order ───────────────────────────────────────
    order = Order(
        order_number=generate_order_number(),
        user_id=user_id,
        customer_name=data["customer_name"].strip(),
        customer_phone=data["customer_phone"].strip(),
        customer_email=data.get("customer_email"),
        customer_address=data.get("customer_address"),
        notes=data.get("notes"),
        source=data.get("source", "website"),
    )
    db.session.add(order)
    db.session.flush()   # get order.id before committing

    # ── Add items ─────────────────────────────────────────
    for item_data in items_data:
        product_id = item_data.get("product_id")
        quantity   = int(item_data.get("quantity", 1))
        if quantity < 1:
            return error_response("Quantity must be at least 1")

        product = Product.query.filter_by(id=product_id, is_active=True).first()
        if not product:
            return error_response(f"Product ID {product_id} not found or unavailable", 422)

        order_item = OrderItem(
            order_id=order.id,
            product_id=product.id,
            product_name=product.name,
            product_image=product.image_url,
            unit_price=product.price,
            quantity=quantity,
        )
        db.session.add(order_item)

    db.session.flush()
    order.calculate_total()
    db.session.commit()

    # ── Notify admin via WhatsApp ─────────────────────────
    wa_result = WhatsAppService.notify_admin_new_order(order)
    if wa_result.get("success"):
        order.wa_notified   = True
        order.wa_message_id = wa_result.get("message_id")
        db.session.commit()

    return success_response(
        data={"order": order.to_dict()},
        message="Order placed successfully! We'll contact you shortly.",
        status_code=201,
    )


def get_my_orders():
    """Return current user's orders (requires JWT)."""
    user_id  = get_jwt_identity()
    page     = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)

    query = Order.query.filter_by(user_id=user_id).order_by(Order.created_at.desc())
    return paginated_response(query, page, per_page, lambda o: o.to_dict(include_items=True))


def get_order_by_number(order_number: str):
    """Look up a single order by its order number (public endpoint)."""
    order = Order.query.filter_by(order_number=order_number).first()
    if not order:
        return error_response("Order not found", 404)
    return success_response(data={"order": order.to_dict()})


# ── Admin controllers ─────────────────────────────────────────────────────────

def admin_get_all_orders():
    page     = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    status   = request.args.get("status")
    source   = request.args.get("source")

    query = Order.query.order_by(Order.created_at.desc())
    if status: query = query.filter(Order.status == status)
    if source: query = query.filter(Order.source == source)

    return paginated_response(query, page, per_page, lambda o: o.to_dict(include_items=True))


def admin_update_order_status(order_id: int):
    order = Order.query.get(order_id)
    if not order:
        return error_response("Order not found", 404)

    data       = request.get_json(silent=True) or {}
    new_status = data.get("status")

    if not new_status or new_status not in Order.VALID_STATUSES:
        return error_response(f"Invalid status. Valid options: {', '.join(Order.VALID_STATUSES)}")

    old_status   = order.status
    order.status = new_status
    db.session.commit()

    # Notify customer on meaningful transitions
    if old_status != new_status and new_status in ("confirmed", "shipped", "delivered", "cancelled"):
        WhatsAppService.notify_status_update(order)

    return success_response(
        data={"order": order.to_dict()},
        message=f"Order status updated to '{new_status}'",
    )


def admin_delete_order(order_id: int):
    order = Order.query.get(order_id)
    if not order:
        return error_response("Order not found", 404)
    db.session.delete(order)
    db.session.commit()
    return success_response(message="Order deleted successfully")
