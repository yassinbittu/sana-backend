from flask import request
from app import db
from app.models.user import User
from app.models.product import Product
from app.models.order import Order
from app.utils.helpers import success_response, error_response, paginated_response


def get_dashboard_stats():
    """Return summary stats for the admin dashboard."""
    total_products  = Product.query.filter_by(is_active=True).count()
    total_orders    = Order.query.count()
    pending_orders  = Order.query.filter_by(status="pending").count()
    total_customers = User.query.filter_by(role="customer").count()

    # Revenue from delivered orders
    delivered = Order.query.filter_by(status="delivered").all()
    total_revenue = sum(float(o.total_amount) for o in delivered)

    # Recent orders (last 5)
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(5).all()

    # Orders by status breakdown
    status_counts = {}
    for status in Order.VALID_STATUSES:
        status_counts[status] = Order.query.filter_by(status=status).count()

    return success_response(data={
        "stats": {
            "total_products":  total_products,
            "total_orders":    total_orders,
            "pending_orders":  pending_orders,
            "total_customers": total_customers,
            "total_revenue":   round(total_revenue, 2),
        },
        "orders_by_status": status_counts,
        "recent_orders": [o.to_dict(include_items=False) for o in recent_orders],
    })


# ── User management ───────────────────────────────────────────────────────────

def get_all_users():
    page     = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    role     = request.args.get("role")

    query = User.query.order_by(User.created_at.desc())
    if role:
        query = query.filter(User.role == role)

    return paginated_response(query, page, per_page, lambda u: u.to_dict())


def get_user(user_id: int):
    user = User.query.get(user_id)
    if not user:
        return error_response("User not found", 404)
    return success_response(data={"user": user.to_dict()})


def toggle_user_status(user_id: int):
    user = User.query.get(user_id)
    if not user:
        return error_response("User not found", 404)
    if user.is_admin():
        return error_response("Cannot deactivate admin account", 403)

    user.is_active = not user.is_active
    db.session.commit()
    status_str = "activated" if user.is_active else "deactivated"
    return success_response(
        data={"user": user.to_dict()},
        message=f"User {status_str} successfully",
    )


def delete_user(user_id: int):
    user = User.query.get(user_id)
    if not user:
        return error_response("User not found", 404)
    if user.is_admin():
        return error_response("Cannot delete admin account", 403)
    db.session.delete(user)
    db.session.commit()
    return success_response(message="User deleted successfully")
