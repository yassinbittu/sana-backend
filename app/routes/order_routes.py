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
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            customer_name:
              type: string
              example: "John Doe"
            customer_email:
              type: string
              example: "john@example.com"
            customer_phone:
              type: string
              example: "+1234567890"
            items:
              type: array
              items:
                type: object
                properties:
                  product_id:
                    type: integer
                    example: 1
                  quantity:
                    type: integer
                    example: 2
    responses:
      201:
        description: Order created
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            message:
              type: string
              example: "Order created successfully"
            data:
              type: object
              properties:
                order_number:
                  type: string
                  example: "ORD-123456"
      400:
        description: Bad request
    """
    return order_controller.create_order()


@order_bp.post("/from-cart")
@jwt_required_custom
def create_order_from_cart():
    """
    Create order from cart
    ---
    tags:
      - Orders
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            customer_name:
              type: string
              example: "John Doe"
            customer_email:
              type: string
              example: "john@example.com"
            customer_phone:
              type: string
              example: "+1234567890"
            customer_address:
              type: string
              example: "123 Main St, City, State"
            notes:
              type: string
              example: "Please deliver between 2-4 PM"
    responses:
      201:
        description: Order created from cart
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            message:
              type: string
              example: "Order placed successfully! We'll contact you shortly."
            data:
              type: object
              properties:
                order:
                  type: object
                  properties:
                    order_number:
                      type: string
                      example: "ORD-123456"
                    customer_name:
                      type: string
                      example: "John Doe"
                    customer_phone:
                      type: string
                      example: "+1234567890"
                    total:
                      type: number
                      example: 5999.98
                    status:
                      type: string
                      example: "pending"
                    items:
                      type: array
                      items:
                        type: object
                        properties:
                          product_name:
                            type: string
                            example: "Beautiful Saree"
                          quantity:
                            type: integer
                            example: 2
                          unit_price:
                            type: number
                            example: 2999.99
                          total:
                            type: number
                            example: 5999.98
      400:
        description: Bad request or empty cart
      401:
        description: Unauthorized
    """
    return order_controller.create_order_from_cart()


@order_bp.get("/track/<string:order_number>")
def track(order_number):
    """
    Track order by order number
    ---
    tags:
      - Orders
    parameters:
      - in: path
        name: order_number
        type: string
        required: true
        example: "ORD-123456"
    responses:
      200:
        description: Order details
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            data:
              type: object
              properties:
                order_number:
                  type: string
                  example: "ORD-123456"
                status:
                  type: string
                  example: "pending"
                customer_name:
                  type: string
                  example: "John Doe"
                items:
                  type: array
                  items:
                    type: object
                    properties:
                      product_name:
                        type: string
                        example: "Laptop"
                      quantity:
                        type: integer
                        example: 2
                      price:
                        type: number
                        example: 999.99
      404:
        description: Order not found
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
    security:
      - Bearer: []
    responses:
      200:
        description: User's orders
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
                  order_number:
                    type: string
                    example: "ORD-123456"
                  status:
                    type: string
                    example: "pending"
                  total:
                    type: number
                    example: 1999.98
                  created_at:
                    type: string
                    example: "2023-10-01T12:00:00Z"
      401:
        description: Unauthorized
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
      - in: query
        name: status
        type: string
        example: "pending"
    responses:
      200:
        description: All orders
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
                  order_number:
                    type: string
                    example: "ORD-123456"
                  status:
                    type: string
                    example: "pending"
                  customer_name:
                    type: string
                    example: "John Doe"
                  total:
                    type: number
                    example: 1999.98
      401:
        description: Unauthorized
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
    security:
      - Bearer: []
    parameters:
      - in: path
        name: order_id
        type: integer
        required: true
        example: 1
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            status:
              type: string
              enum: ["pending", "processing", "shipped", "delivered", "cancelled"]
              example: "shipped"
    responses:
      200:
        description: Status updated
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            message:
              type: string
              example: "Order status updated successfully"
      400:
        description: Bad request
      401:
        description: Unauthorized
      404:
        description: Order not found
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
    security:
      - Bearer: []
    parameters:
      - in: path
        name: order_id
        type: integer
        required: true
        example: 1
    responses:
      200:
        description: Order deleted
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            message:
              type: string
              example: "Order deleted successfully"
      401:
        description: Unauthorized
      404:
        description: Order not found
    """
    return order_controller.admin_delete_order(order_id)