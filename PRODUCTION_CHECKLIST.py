"""
Production Login Troubleshooting Checklist
"""
import os
import json
from app import create_app

app = create_app()

print("\n" + "="*70)
print("🚀 PRODUCTION DEPLOYMENT CHECKLIST")
print("="*70)

with app.app_context():
    print("\n1️⃣  ENVIRONMENT VARIABLES:")
    print("   These MUST be set in production:")
    
    env_vars = {
        "FLASK_ENV": os.getenv("FLASK_ENV"),
        "SECRET_KEY": os.getenv("SECRET_KEY", "NOT SET"),
        "JWT_SECRET_KEY": os.getenv("JWT_SECRET_KEY", "NOT SET"),
        "DATABASE_URL": os.getenv("DATABASE_URL", "NOT SET")[:50] + "...",
        "ADMIN_EMAIL": os.getenv("ADMIN_EMAIL"),
        "ADMIN_PASSWORD": os.getenv("ADMIN_PASSWORD", "NOT SET"),
        "ADMIN_USERNAME": os.getenv("ADMIN_USERNAME"),
    }
    
    for key, value in env_vars.items():
        status = "✅" if value and value != "NOT SET" else "❌"
        print(f"   {status} {key}: {value}")
    
    print("\n2️⃣  FLASK CONFIGURATION:")
    flask_config = {
        "DEBUG": app.config.get("DEBUG"),
        "TESTING": app.config.get("TESTING"),
        "JWT_HEADER_NAME": app.config.get("JWT_HEADER_NAME"),
        "JWT_HEADER_TYPE": f"'{app.config.get('JWT_HEADER_TYPE')}'",
    }
    for key, value in flask_config.items():
        print(f"   {key}: {value}")
    
    print("\n3️⃣  COMMON PRODUCTION ISSUES:")
    print("""
   🔴 Issue 1: Different database in production
      Solution: Verify DATABASE_URL points to correct Supabase instance
      
   🔴 Issue 2: JWT_SECRET_KEY not set or different
      Solution: Set JWT_SECRET_KEY to a strong, consistent value
      
   🔴 Issue 3: CORS blocking requests
      Solution: Check FRONTEND_URL matches your production frontend
      
   🔴 Issue 4: Admin user not in production database
      Solution: Run migrations and ensure admin bootstrap runs on startup
      
   🔴 Issue 5: Content-Type header missing from client
      Solution: Client must send: Content-Type: application/json
    """)
    
    print("\n4️⃣  VERIFICATION COMMANDS:")
    print("""
    For your hosting platform (Vercel/Railway/Render/etc), run:
    
    1. Check environment variables are loaded:
       python -c "import os; print('JWT_SECRET_KEY set:', bool(os.getenv('JWT_SECRET_KEY')))"
    
    2. Test login endpoint:
       curl -X POST https://your-api.com/api/auth/login \\
         -H "Content-Type: application/json" \\
         -d '{"email":"iamyxn12@gmail.com","password":"admin123"}'
    
    3. Check logs for specific error:
       Look for 401 error details in production logs
    """)

print("\n" + "="*70 + "\n")

# Create a template for production .env
production_env_template = """
# ════════════════════════════════════════════════════════════════════
# 🔐 PRODUCTION ENVIRONMENT VARIABLES
# ════════════════════════════════════════════════════════════════════

# ── Flask ──────────────────────────────────────────────
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=generate-a-strong-random-key-here

# ── Database ────────────────────────────────────────────
# IMPORTANT: Use the SAME Supabase instance for production
DATABASE_URL=postgresql+psycopg://user:password@host:port/database

# ── JWT ─────────────────────────────────────────────────
# IMPORTANT: Set a strong, secure key and keep it consistent
JWT_SECRET_KEY=generate-a-strong-random-jwt-key-here
JWT_ACCESS_TOKEN_EXPIRES=3600
JWT_REFRESH_TOKEN_EXPIRES=2592000

# ── Admin ────────────────────────────────────────────────
ADMIN_USERNAME=admin
ADMIN_PASSWORD=change-to-strong-password-in-production
ADMIN_EMAIL=iamyxn12@gmail.com

# ── Email ───────────────────────────────────────────────
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USE_SSL=False
MAIL_USERNAME=iamyxn12@gmail.com
MAIL_PASSWORD=your-gmail-app-password

# ── File Upload ──────────────────────────────────────────
UPLOAD_FOLDER=app/uploads
MAX_CONTENT_LENGTH=5242880
ALLOWED_EXTENSIONS=png,jpg,jpeg,gif,webp

# ── WhatsApp ─────────────────────────────────────────────
WHATSAPP_PHONE_NUMBER=917799296786
WHATSAPP_API_TOKEN=your-whatsapp-token
WHATSAPP_VERIFY_TOKEN=your-webhook-verify-token

# ── CORS ─────────────────────────────────────────────────
# IMPORTANT: Set to your production frontend URL(s)
FRONTEND_URL=https://your-frontend-domain.com,https://www.your-frontend-domain.com

# ── PORT ─────────────────────────────────────────────────
PORT=5000
"""

print("📝 Save this template as your production .env file:\n")
print(production_env_template)
