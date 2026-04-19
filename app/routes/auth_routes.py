from flask import Blueprint
from app.controllers import auth_controller

auth_bp = Blueprint("auth", __name__)


@auth_bp.post("/register")
def register():
    """
    Register new user - sends OTP for email verification
    ---
    tags:
      - Auth
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            username:
              type: string
              example: "johndoe"
            email:
              type: string
              example: "john@example.com"
            password:
              type: string
              example: "password123"
            phone:
              type: string
              example: "+1234567890"
    responses:
      200:
        description: OTP sent to email
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            message:
              type: string
              example: "Verification OTP sent to your email. Please check your inbox."
            data:
              type: object
              properties:
                email:
                  type: string
                  example: "john@example.com"
      400:
        description: Bad request
      409:
        description: Email or username already exists
      500:
        description: Failed to send email
    """
    return auth_controller.register()


@auth_bp.post("/login")
def login():
    """
    Login user or admin
    ---
    tags:
      - Auth
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            email:
              type: string
              example: "iamyxn12@gmail.com"
            password:
              type: string
              example: "admin123"
    responses:
      200:
        description: Login successful
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            message:
              type: string
              example: "Login successful"
            data:
              type: object
              properties:
                user:
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
                      example: "customer"
                    is_active:
                      type: boolean
                      example: true
                access_token:
                  type: string
                  example: "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
                refresh_token:
                  type: string
                  example: "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
      401:
        description: Invalid credentials
    """
    return auth_controller.login()


@auth_bp.post("/refresh")
def refresh():
    """
    Refresh JWT token
    ---
    tags:
      - Auth
    security:
      - Bearer: []
    responses:
      200:
        description: Token refreshed
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            message:
              type: string
              example: "Token refreshed"
            data:
              type: object
              properties:
                access_token:
                  type: string
                  example: "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
      401:
        description: Invalid or expired refresh token
    """
    return auth_controller.refresh_token()


@auth_bp.get("/me")
def profile():
    """
    Get user profile
    ---
    tags:
      - Auth
    security:
      - Bearer: []
    responses:
      200:
        description: User profile
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
      401:
        description: Unauthorized
    """
    return auth_controller.get_profile()


@auth_bp.post("/verify-otp")
def verify_otp():
    """
    Verify OTP and complete registration
    ---
    tags:
      - Auth
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            email:
              type: string
              example: "john@example.com"
            otp:
              type: string
              example: "123456"
            username:
              type: string
              example: "johndoe"
            password:
              type: string
              example: "password123"
            phone:
              type: string
              example: "+1234567890"
    responses:
      201:
        description: Account created successfully
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            message:
              type: string
              example: "Account verified and created successfully"
            data:
              type: object
              properties:
                user:
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
                      example: "customer"
                access_token:
                  type: string
                  example: "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
                refresh_token:
                  type: string
                  example: "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
      400:
        description: Invalid or expired OTP
    """
    return auth_controller.verify_otp()