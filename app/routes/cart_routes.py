from flask import Blueprint
from app.controllers import cart_controller

cart_bp = Blueprint("cart", __name__)


@cart_bp.get("")
def get_cart():
    """
    Get guest cart
    ---
    tags:
      - Cart
    responses:
      200:
        description: Cart items retrieved successfully
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            data:
              type: object
              properties:
                items:
                  type: array
                  items:
                    type: object
                    properties:
                      id:
                        type: integer
                        example: 1
                      product:
                        type: object
                        properties:
                          id:
                            type: integer
                            example: 1
                          name:
                            type: string
                            example: "Beautiful Saree"
                          price:
                            type: number
                            example: 2999.99
                          image_url:
                            type: string
                            example: "/uploads/products/saree.jpg"
                      quantity:
                        type: integer
                        example: 2
                      subtotal:
                        type: number
                        example: 5999.98
                      discount_amount:
                        type: number
                        example: 300.00
                      total:
                        type: number
                        example: 5699.98
                summary:
                  type: object
                  properties:
                    item_count:
                      type: integer
                      example: 3
                    subtotal:
                      type: number
                      example: 8999.97
                    discount_total:
                      type: number
                      example: 450.00
                    total:
                      type: number
                      example: 8549.97
    """
    return cart_controller.get_cart()


@cart_bp.post("/add")
def add_to_cart():
    """
    Add product to cart
    ---
    tags:
      - Cart
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            product_id:
              type: integer
              example: 1
            quantity:
              type: integer
              example: 1
              default: 1
    responses:
      200:
        description: Product added to cart (existing item updated)
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            message:
              type: string
              example: "Cart updated successfully"
            data:
              type: object
              properties:
                cart_item:
                  type: object
                  properties:
                    id:
                      type: integer
                      example: 1
                    product:
                      type: object
                      properties:
                        id:
                          type: integer
                          example: 1
                        name:
                          type: string
                          example: "Beautiful Saree"
                    quantity:
                      type: integer
                      example: 3
      201:
        description: Product added to cart (new item created)
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            message:
              type: string
              example: "Product added to cart successfully"
            data:
              type: object
              properties:
                cart_item:
                  type: object
                  properties:
                    id:
                      type: integer
                      example: 2
                    product:
                      type: object
                      properties:
                        id:
                          type: integer
                          example: 1
                        name:
                          type: string
                          example: "Beautiful Saree"
                    quantity:
                      type: integer
                      example: 1
      400:
        description: Bad request
      404:
        description: Product not found
    """
    return cart_controller.add_to_cart()


@cart_bp.put("/item/<int:cart_item_id>")
def update_cart_item(cart_item_id):
    """
    Update cart item quantity
    ---
    tags:
      - Cart
    parameters:
      - in: path
        name: cart_item_id
        type: integer
        required: true
        example: 1
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            quantity:
              type: integer
              example: 3
    responses:
      200:
        description: Cart item updated successfully
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            message:
              type: string
              example: "Cart item updated successfully"
            data:
              type: object
              properties:
                cart_item:
                  type: object
                  properties:
                    id:
                      type: integer
                      example: 1
                    quantity:
                      type: integer
                      example: 3
                    total:
                      type: number
                      example: 8999.97
      400:
        description: Bad request
      404:
        description: Cart item not found
    """
    return cart_controller.update_cart_item(cart_item_id)


@cart_bp.delete("/item/<int:cart_item_id>")
def remove_from_cart(cart_item_id):
    """
    Remove item from cart
    ---
    tags:
      - Cart
    parameters:
      - in: path
        name: cart_item_id
        type: integer
        required: true
        example: 1
    responses:
      200:
        description: Item removed from cart
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            message:
              type: string
              example: "Item removed from cart successfully"
      404:
        description: Cart item not found
    """
    return cart_controller.remove_from_cart(cart_item_id)


@cart_bp.delete("/clear")
def clear_cart():
    """
    Clear all items from cart
    ---
    tags:
      - Cart
    responses:
      200:
        description: Cart cleared successfully
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            message:
              type: string
              example: "Cart cleared successfully"
    """
    return cart_controller.clear_cart()


@cart_bp.get("/count")
def get_cart_count():
    """
    Get cart item count
    ---
    tags:
      - Cart
    responses:
      200:
        description: Cart count retrieved
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            data:
              type: object
              properties:
                count:
                  type: integer
                  example: 5
    """
    return cart_controller.get_cart_count()
