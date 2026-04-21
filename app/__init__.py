import os
import sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from flasgger import Swagger
from dotenv import load_dotenv

# Add project root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

from config import get_config

# Extensions
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
bcrypt = Bcrypt()
mail = Mail()


def create_app(config_class=None):
    app = Flask(__name__, static_folder="uploads", static_url_path="/uploads")

    # ───────── Swagger Template ─────────
    swagger_template = {
        "swagger": "2.0",
        "info": {
            "title": "SANA API",
            "description": "SANA Sarees Backend API Documentation",
            "version": "1.0.0"
        },
        "basePath": "/",
        "schemes": ["http", "https"],
        "securityDefinitions": {
            "Bearer": {
                "type": "apiKey",
                "name": "Authorization",
                "in": "header",
                "description": "JWT Authorization header using Bearer token"
            }
        }
    }

    # ───────── Swagger Config (MULTI MODULE) ─────────
    swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'auth_spec',
            "route": '/apispec/auth.json',
            "rule_filter": lambda rule: rule.rule.startswith('/api/auth'),
            "model_filter": lambda tag: True,
        },
        {
            "endpoint": 'product_spec',
            "route": '/apispec/products.json',
            "rule_filter": lambda rule: rule.rule.startswith('/api/products'),
            "model_filter": lambda tag: True,
        },
        {
            "endpoint": 'cart_spec',
            "route": '/apispec/cart.json',
            "rule_filter": lambda rule: rule.rule.startswith('/api/cart'),
            "model_filter": lambda tag: True,
        },
        {
            "endpoint": 'order_spec',
            "route": '/apispec/orders.json',
            "rule_filter": lambda rule: rule.rule.startswith('/api/orders'),
            "model_filter": lambda tag: True,
        },
        {
            "endpoint": 'admin_spec',
            "route": '/apispec/admin.json',
            "rule_filter": lambda rule: rule.rule.startswith('/api/admin'),
            "model_filter": lambda tag: True,
        },
        {
            "endpoint": 'upload_spec',
            "route": '/apispec/upload.json',
            "rule_filter": lambda rule: rule.rule.startswith('/api/upload'),
            "model_filter": lambda tag: True,
        },
        {
            "endpoint": 'whatsapp_spec',
            "route": '/apispec/whatsapp.json',
            "rule_filter": lambda rule: rule.rule.startswith('/api/whatsapp'),
            "model_filter": lambda tag: True,
        }
    ],

    # 🔥 THIS ENABLES DROPDOWN
    "urls": [
        {"url": "/apispec/auth.json", "name": "Auth API"},
        {"url": "/apispec/products.json", "name": "Products API"},
        {"url": "/apispec/cart.json", "name": "Cart API"},
        {"url": "/apispec/orders.json", "name": "Orders API"},
        {"url": "/apispec/admin.json", "name": "Admin API"},
        {"url": "/apispec/upload.json", "name": "Upload API"},
        {"url": "/apispec/whatsapp.json", "name": "WhatsApp API"}
    ],

    "swagger_ui": True,
    "specs_route": "/apidocs/",

    # 🔥 CRITICAL FIX
    "swagger_ui_parameters": {
        "urls.primaryName": "Auth API",
        "docExpansion": "list",
        "displayOperationId": True
    }
}

    Swagger(app, config=swagger_config, template=swagger_template)

    # ───────── Config ─────────
    if config_class is None:
        config_class = get_config()

    app.config.from_object(config_class)

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # Ensure DATABASE_URL is set
    if not app.config.get('SQLALCHEMY_DATABASE_URI'):
        raise ValueError("DATABASE_URL environment variable is not set. Please check your .env file.")

    # Debug print
    if app.debug:
        print(f"Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")

    # Init extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    bcrypt.init_app(app)
    mail.init_app(app)

    with app.app_context():
        from app.services.admin_bootstrap import ensure_admin_user

        ensure_admin_user(app)

    # CORS
    allowed_origins = [origin.strip() for origin in app.config["FRONTEND_URL"].split(",") if origin.strip()]
    if "http://localhost:5173" not in allowed_origins:
        allowed_origins.append("http://localhost:5173")

    CORS(app, resources={
        r"/api/*": {
            "origins": allowed_origins,
            "methods": ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True,
        },
        r"/uploads/*": {
            "origins": allowed_origins,
            "methods": ["GET", "OPTIONS"],
            "allow_headers": ["Content-Type"],
            "supports_credentials": False,
        }
    })

    # Blueprints
    from app.routes.auth_routes import auth_bp
    from app.routes.product_routes import product_bp
    from app.routes.cart_routes import cart_bp
    from app.routes.order_routes import order_bp
    from app.routes.admin_routes import admin_bp
    from app.routes.upload_routes import upload_bp
    from app.routes.whatsapp_routes import whatsapp_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(product_bp, url_prefix="/api/products")
    app.register_blueprint(cart_bp, url_prefix="/api/cart")
    app.register_blueprint(order_bp, url_prefix="/api/orders")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")
    app.register_blueprint(upload_bp, url_prefix="/api/upload")
    app.register_blueprint(whatsapp_bp, url_prefix="/api/whatsapp")

    return app
