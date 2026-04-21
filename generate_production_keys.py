"""
Secure Production Key Generator
Generates secure SECRET_KEY and JWT_SECRET_KEY for production
"""
import secrets
import os

print("\n" + "="*70)
print("🔐 SECURE PRODUCTION KEY GENERATOR")
print("="*70)

# Generate SECRET_KEY
secret_key = secrets.token_hex(32)
jwt_secret_key = secrets.token_hex(32)

print("\n✅ GENERATED SECURE KEYS FOR PRODUCTION:\n")
print("SECRET_KEY:")
print(f"  {secret_key}\n")

print("JWT_SECRET_KEY:")
print(f"  {jwt_secret_key}\n")

print("="*70)
print("\n📋 PRODUCTION .env VALUES TO SET:\n")

production_env = f"""# ── Flask ──────────────────────────────────────────────
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY={secret_key}

# ── Database ────────────────────────────────────────────
DATABASE_URL=postgresql+psycopg://postgres.cxsjnwqoybfoxpkdqwpo:S%40nasarees_@aws-1-ap-northeast-1.pooler.supabase.com:5432/postgres

# ── JWT ─────────────────────────────────────────────────
JWT_SECRET_KEY={jwt_secret_key}
JWT_ACCESS_TOKEN_EXPIRES=3600
JWT_REFRESH_TOKEN_EXPIRES=2592000

# ── Admin ────────────────────────────────────────────────
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123
ADMIN_EMAIL=iamyxn12@gmail.com

# ── Email ───────────────────────────────────────────────
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USE_SSL=False
MAIL_USERNAME=iamyxn12@gmail.com
MAIL_PASSWORD=yassinbittu12
MAIL_DEFAULT_SENDER=iamyxn12@gmail.com

# ── File Upload ──────────────────────────────────────────
UPLOAD_FOLDER=app/uploads
MAX_CONTENT_LENGTH=5242880
ALLOWED_EXTENSIONS=png,jpg,jpeg,gif,webp

# ── WhatsApp ─────────────────────────────────────────────
WHATSAPP_PHONE_NUMBER=917799296786
WHATSAPP_API_TOKEN=your-whatsapp-token
WHATSAPP_VERIFY_TOKEN=your-webhook-verify-token

# ── CORS ─────────────────────────────────────────────────
FRONTEND_URL=https://sanasarees-olive.vercel.app,https://sanasarees-j4gfqq9c3-yassinbittus-projects.vercel.app,http://localhost:5173
"""

print(production_env)

print("="*70)
print("\n📌 NEXT STEPS:")
print("""
1. Copy the production .env values above
2. Go to: https://vercel.com/dashboard
3. Select your project
4. Go to Settings → Environment Variables
5. Update these values:
   - FLASK_ENV = production
   - FLASK_DEBUG = False
   - SECRET_KEY = (paste the generated key above)
   - JWT_SECRET_KEY = (paste the generated key above)
6. Redeploy your app
7. Test login again
""")

print("="*70 + "\n")
