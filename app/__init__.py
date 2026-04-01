import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flasgger import Swagger
from dotenv import load_dotenv

from config import get_config

# Load .env
load_dotenv()

# ── Extensions ──────────────────────────────────────────
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
bcrypt = Bcrypt()


def create_app(config_class=None):
    app = Flask(__name__, static_folder="uploads", static_url_path="/uploads")

    # ── Swagger Config ───────────────────────────────────
    swagger_config = {
        "headers": [],
        "specs": [
            {
                "endpoint": 'apispec',
                "route": '/apispec.json',
                "rule_filter": lambda rule: True,
                "model_filter": lambda tag: True,
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/apidocs/"
    }
    Swagger(app, config=swagger_config)

    # ── Config ───────────────────────────────────────────
    if config_class is None:
        config_class = get_config()
    app.config.from_object(config_class)

    # ── Upload directory ─────────────────────────────────
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # ── Init extensions ──────────────────────────────────
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    bcrypt.init_app(app)

    # ── CORS ─────────────────────────────────────────────
    CORS(app, resources={
        r"/api/*": {
            "origins": [app.config["FRONTEND_URL"], "http://localhost:5173"],
            "methods": ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True,
        }
    })

    # ── JWT error handlers ───────────────────────────────
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return {"success": False, "message": "Token has expired"}, 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return {"success": False, "message": "Invalid token"}, 401

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return {"success": False, "message": "Authorization token is missing"}, 401

    # ── Register blueprints ──────────────────────────────
    from app.routes.auth_routes import auth_bp
    from app.routes.product_routes import product_bp
    from app.routes.order_routes import order_bp
    from app.routes.admin_routes import admin_bp
    from app.routes.upload_routes import upload_bp
    from app.routes.whatsapp_routes import whatsapp_bp

    app.register_blueprint(auth_bp,      url_prefix="/api/auth")
    app.register_blueprint(product_bp,   url_prefix="/api/products")
    app.register_blueprint(order_bp,     url_prefix="/api/orders")
    app.register_blueprint(admin_bp,     url_prefix="/api/admin")
    app.register_blueprint(upload_bp,    url_prefix="/api/upload")
    app.register_blueprint(whatsapp_bp,  url_prefix="/api/whatsapp")

    # ── Health check ─────────────────────────────────────
    @app.get("/api/health")
    def health():
        """
        API Health Check
        ---
        tags:
          - Health
        responses:
          200:
            description: API is running
        """
        return {"success": True, "message": "SANA API is running 🚀", "version": "1.0.0"}

    # ── Seed admin on first run ──────────────────────────
    with app.app_context():
        db.create_all()
        _seed_admin(app)

    return app


def _seed_admin(app):
    """Create default admin user if none exists."""
    from app.models.user import User
    if not User.query.filter_by(role="admin").first():
        admin = User(
            username=app.config["ADMIN_USERNAME"],
            email=app.config["ADMIN_EMAIL"],
            role="admin",
        )
        admin.set_password(app.config["ADMIN_PASSWORD"])
        db.session.add(admin)
        db.session.commit()
        print(f"[SEED] Admin user created → {app.config['ADMIN_EMAIL']}")