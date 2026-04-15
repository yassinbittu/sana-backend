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
    security:
      - Bearer: []
    responses:
      200:
        description: Dashboard stats
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            data:
              type: object
              properties:
                total_users:
                  type: integer
                  example: 150
                total_products:
                  type: integer
                  example: 50
                total_orders:
                  type: integer
                  example: 200
                recent_orders:
                  type: array
                  items:
                    type: object
                    properties:
                      order_number:
                        type: string
                        example: "ORD-123456"
                      status:
                        type: string
                        example: "pending"
      401:
        description: Unauthorized
    """
    return admin_controller.get_dashboard_stats()


@admin_bp.get("/users")
def users():
    """
    Get all users
    ---
    tags:
      - Admin
    security:
      - Bearer: []
    parameters:
      - in: query
        name: page
        type: integer
        example: 1
      - in: query
        name: limit
        type: integer
        example: 10
    responses:
      200:
        description: List of users
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            data:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: integer
                    example: 1
                  username:
                    type: string
                    example: "johndoe"
                  email:
                    type: string
                    example: "john@example.com"
                  role:
                    type: string
                    example: "user"
                  is_active:
                    type: boolean
                    example: true
      401:
        description: Unauthorized
    """
    return admin_controller.get_all_users()


@admin_bp.get("/users/<int:user_id>")
def user(user_id):
    """
    Get user by ID
    ---
    tags:
      - Admin
    security:
      - Bearer: []
    parameters:
      - in: path
        name: user_id
        type: integer
        required: true
        example: 1
    responses:
      200:
        description: User details
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            data:
              type: object
              properties:
                id:
                  type: integer
                  example: 1
                username:
                  type: string
                  example: "johndoe"
                email:
                  type: string
                  example: "john@example.com"
                role:
                  type: string
                  example: "user"
                is_active:
                  type: boolean
                  example: true
      401:
        description: Unauthorized
      404:
        description: User not found
    """
    return admin_controller.get_user(user_id)


@admin_bp.patch("/users/<int:user_id>/toggle")
def toggle(user_id):
    """
    Toggle user status
    ---
    tags:
      - Admin
    security:
      - Bearer: []
    parameters:
      - in: path
        name: user_id
        type: integer
        required: true
        example: 1
    responses:
      200:
        description: User status toggled
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            message:
              type: string
              example: "User status updated successfully"
      401:
        description: Unauthorized
      404:
        description: User not found
    """
    return admin_controller.toggle_user_status(user_id)


@admin_bp.delete("/users/<int:user_id>")
def delete_user(user_id):
    """
    Delete user
    ---
    tags:
      - Admin
    security:
      - Bearer: []
    parameters:
      - in: path
        name: user_id
        type: integer
        required: true
        example: 1
    responses:
      200:
        description: User deleted
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            message:
              type: string
              example: "User deleted successfully"
      401:
        description: Unauthorized
      404:
        description: User not found
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