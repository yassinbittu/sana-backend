from flask import Blueprint
from app.controllers import product_controller
from app.middleware.auth_middleware import admin_required

product_bp = Blueprint("products", __name__)


@product_bp.get("")
def get_products():
    """
    Get all products with filtering and pagination
    ---
    tags:
      - Products
    parameters:
      - in: query
        name: page
        type: integer
        example: 1
        description: Page number for pagination
      - in: query
        name: per_page
        type: integer
        example: 12
        description: Number of products per page (max 50)
      - in: query
        name: occasion
        type: string
        example: "Wedding"
        description: Filter by occasion
      - in: query
        name: fabric
        type: string
        example: "Silk"
        description: Filter by fabric type
      - in: query
        name: color
        type: string
        example: "Red"
        description: Filter by color
      - in: query
        name: in_stock
        type: boolean
        example: true
        description: Filter by stock availability
      - in: query
        name: is_new
        type: boolean
        example: false
        description: Filter by new arrivals
      - in: query
        name: min_price
        type: number
        example: 100.0
        description: Minimum price filter
      - in: query
        name: max_price
        type: number
        example: 1000.0
        description: Maximum price filter
      - in: query
        name: search
        type: string
        example: "saree"
        description: Search in product name and description
      - in: query
        name: sort
        type: string
        enum: ["newest", "price_asc", "price_desc"]
        example: "newest"
        description: Sort order
    responses:
      200:
        description: List of products with pagination
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            data:
              type: object
              properties:
                products:
                  type: array
                  items:
                    type: object
                    properties:
                      id:
                        type: integer
                        example: 1
                      name:
                        type: string
                        example: "Red Silk Saree"
                      description:
                        type: string
                        example: "Beautiful red silk saree for weddings"
                      price:
                        type: number
                        example: 2999.99
                      original_price:
                        type: number
                        example: 3999.99
                      discount:
                        type: integer
                        example: 25
                      discount_amount:
                        type: number
                        example: 1000.0
                      image_url:
                        type: string
                        example: "/uploads/products/saree1.jpg"
                      occasion:
                        type: string
                        example: "Wedding"
                      fabric:
                        type: string
                        example: "Silk"
                      color:
                        type: string
                        example: "Red"
                      care:
                        type: string
                        example: "Dry clean only"
                      in_stock:
                        type: boolean
                        example: true
                      is_new:
                        type: boolean
                        example: false
                      created_at:
                        type: string
                        example: "2026-04-01T10:00:00Z"
                pagination:
                  type: object
                  properties:
                    page:
                      type: integer
                      example: 1
                    per_page:
                      type: integer
                      example: 12
                    total:
                      type: integer
                      example: 150
                    pages:
                      type: integer
                      example: 13
                    has_next:
                      type: boolean
                      example: true
                    has_prev:
                      type: boolean
                      example: false
    """
    return product_controller.get_all_products()


@product_bp.get("/filters")
def get_filters():
    """
    Get product filters (distinct values for dropdowns)
    ---
    tags:
      - Products
    responses:
      200:
        description: Product filters for frontend dropdowns
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            data:
              type: object
              properties:
                occasions:
                  type: array
                  items:
                    type: string
                  example: ["Wedding", "Festival", "Party", "Casual"]
                  description: Available occasion types
                fabrics:
                  type: array
                  items:
                    type: string
                  example: ["Silk", "Cotton", "Chiffon", "Georgette"]
                  description: Available fabric types
                colors:
                  type: array
                  items:
                    type: string
                  example: ["Red", "Blue", "Green", "Black", "White"]
                  description: Available colors
    """
    return product_controller.get_product_filters()


@product_bp.get("/<int:product_id>")
def get_product(product_id):
    """
    Get product by ID
    ---
    tags:
      - Products
    parameters:
      - in: path
        name: product_id
        type: integer
        required: true
        example: 1
    responses:
      200:
        description: Product details
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            data:
              type: object
              properties:
                product:
                  type: object
                  properties:
                    id:
                      type: integer
                      example: 1
                    name:
                      type: string
                      example: "Red Silk Saree"
                    description:
                      type: string
                      example: "Beautiful red silk saree for weddings"
                    price:
                      type: number
                      example: 2999.99
                    original_price:
                      type: number
                      example: 3999.99
                    discount:
                      type: integer
                      example: 25
                    discount_amount:
                      type: number
                      example: 1000.0
                    image_url:
                      type: string
                      example: "/uploads/products/saree1.jpg"
                    occasion:
                      type: string
                      example: "Wedding"
                    fabric:
                      type: string
                      example: "Silk"
                    color:
                      type: string
                      example: "Red"
                    care:
                      type: string
                      example: "Dry clean only"
                    in_stock:
                      type: boolean
                      example: true
                    is_new:
                      type: boolean
                      example: false
                    created_at:
                      type: string
                      example: "2026-04-01T10:00:00Z"
                    updated_at:
                      type: string
                      example: "2026-04-01T10:00:00Z"
      404:
        description: Product not found
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
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            name:
              type: string
              required: true
              example: "Red Silk Saree"
              description: Product name
            description:
              type: string
              example: "Beautiful red silk saree for weddings"
              description: Product description
            price:
              type: number
              required: true
              example: 2999.99
              description: Current selling price
            original_price:
              type: number
              example: 3999.99
              description: Original price (optional, used for discount calculation)
            image_url:
              type: string
              example: "/uploads/products/saree1.jpg"
              description: Product image URL
            occasion:
              type: string
              example: "Wedding"
              description: Occasion type (Wedding, Festival, etc.)
            fabric:
              type: string
              example: "Silk"
              description: Fabric material
            color:
              type: string
              example: "Red"
              description: Product color
            care:
              type: string
              example: "Dry clean only"
              description: Care instructions
            in_stock:
              type: boolean
              example: true
              description: Stock availability
            is_new:
              type: boolean
              example: false
              description: Mark as new arrival
      - in: formData
        name: image
        type: file
        description: Product image file (alternative to image_url)
    responses:
      201:
        description: Product created
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            message:
              type: string
              example: "Product created successfully"
            data:
              type: object
              properties:
                product:
                  type: object
                  properties:
                    id:
                      type: integer
                      example: 2
                    name:
                      type: string
                      example: "Red Silk Saree"
                    description:
                      type: string
                      example: "Beautiful red silk saree for weddings"
                    price:
                      type: number
                      example: 2999.99
                    original_price:
                      type: number
                      example: 3999.99
                    discount:
                      type: integer
                      example: 25
                    discount_amount:
                      type: number
                      example: 1000.0
                    image_url:
                      type: string
                      example: "/uploads/products/saree1.jpg"
                    occasion:
                      type: string
                      example: "Wedding"
                    fabric:
                      type: string
                      example: "Silk"
                    color:
                      type: string
                      example: "Red"
                    care:
                      type: string
                      example: "Dry clean only"
                    in_stock:
                      type: boolean
                      example: true
                    is_new:
                      type: boolean
                      example: false
                    created_at:
                      type: string
                      example: "2026-04-01T10:00:00Z"
      400:
        description: Bad request
      401:
        description: Unauthorized
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
    security:
      - Bearer: []
    parameters:
      - in: path
        name: product_id
        type: integer
        required: true
        example: 1
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            name:
              type: string
              example: "Updated Red Silk Saree"
              description: Product name
            description:
              type: string
              example: "Updated description for the saree"
              description: Product description
            price:
              type: number
              example: 2499.99
              description: Current selling price
            original_price:
              type: number
              example: 3499.99
              description: Original price (optional, used for discount calculation)
            image_url:
              type: string
              example: "/uploads/products/updated-saree.jpg"
              description: Product image URL
            occasion:
              type: string
              example: "Festival"
              description: Occasion type (Wedding, Festival, etc.)
            fabric:
              type: string
              example: "Cotton Silk"
              description: Fabric material
            color:
              type: string
              example: "Maroon"
              description: Product color
            care:
              type: string
              example: "Hand wash only"
              description: Care instructions
            in_stock:
              type: boolean
              example: true
              description: Stock availability
            is_new:
              type: boolean
              example: true
              description: Mark as new arrival
            is_active:
              type: boolean
              example: true
              description: Product active status
      - in: formData
        name: image
        type: file
        description: Product image file (alternative to image_url)
    responses:
      200:
        description: Product updated
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            message:
              type: string
              example: "Product updated successfully"
            data:
              type: object
              properties:
                product:
                  type: object
                  properties:
                    id:
                      type: integer
                      example: 1
                    name:
                      type: string
                      example: "Updated Red Silk Saree"
                    description:
                      type: string
                      example: "Updated description for the saree"
                    price:
                      type: number
                      example: 2499.99
                    original_price:
                      type: number
                      example: 3499.99
                    discount:
                      type: integer
                      example: 29
                    discount_amount:
                      type: number
                      example: 1000.0
                    image_url:
                      type: string
                      example: "/uploads/products/updated-saree.jpg"
                    occasion:
                      type: string
                      example: "Festival"
                    fabric:
                      type: string
                      example: "Cotton Silk"
                    color:
                      type: string
                      example: "Maroon"
                    care:
                      type: string
                      example: "Hand wash only"
                    in_stock:
                      type: boolean
                      example: true
                    is_new:
                      type: boolean
                      example: true
                    updated_at:
                      type: string
                      example: "2026-04-01T11:00:00Z"
      400:
        description: Bad request
      401:
        description: Unauthorized
      404:
        description: Product not found
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
    security:
      - Bearer: []
    parameters:
      - in: path
        name: product_id
        type: integer
        required: true
        example: 1
    responses:
      200:
        description: Product deleted
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            message:
              type: string
              example: "Product deleted successfully"
      401:
        description: Unauthorized
      404:
        description: Product not found
    """
    return product_controller.delete_product(product_id)