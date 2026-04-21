# 🚀 Production Deployment Guide - Fix 401 Login Error

## What's Happening

- ✅ **Local environment**: Login works perfectly (200 OK)
- ❌ **Production environment**: Getting 401 Unauthorized

## Root Cause

Your production environment is missing or has incorrect environment variables. The most likely culprits:

### 1. **JWT_SECRET_KEY & SECRET_KEY Not Set**
If these are placeholder values or different between local and production, token validation fails.

### 2. **Wrong Database Connection**
If production is pointing to a different database than where the admin user exists.

### 3. **Missing Admin User in Production DB**
Admin might not exist in production database if migrations didn't run.

---

## 🛠️ Fix for Different Hosting Platforms

### If you're using **Vercel**, **Railway**, **Render**, or **Heroku**:

1. **Go to your deployment dashboard environment variables**
2. **Add/Update these variables:**

```env
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=your-super-secure-key-here-min-32-chars
JWT_SECRET_KEY=your-jwt-secret-key-here-min-32-chars
DATABASE_URL=postgresql+psycopg://your:password@host:port/database
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123
ADMIN_EMAIL=iamyxn12@gmail.com
FRONTEND_URL=https://your-frontend-domain.com
```

3. **Generate secure keys (don't use placeholders!)**
   
   Use Python to generate:
   ```python
   import secrets
   print("SECRET_KEY:", secrets.token_hex(32))
   print("JWT_SECRET_KEY:", secrets.token_hex(32))
   ```

4. **Redeploy your application**

### If you're using a **Traditional VPS/Server**:

1. **SSH into your production server**
2. **Update `.env` file** with actual values (not placeholders)
3. **Restart the app:**
   ```bash
   # If using systemd
   sudo systemctl restart your-app-name
   
   # If using PM2
   pm2 restart sana-backend
   
   # If using Docker
   docker-compose restart
   ```

---

## 🧪 Test After Deployment

Once you've set the environment variables and redeployed:

### Test from your local machine:
```bash
curl -X POST https://your-api-domain.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "iamyxn12@gmail.com",
    "password": "admin123"
  }'
```

**Expected response (200 OK):**
```json
{
  "success": true,
  "message": "Login successful",
  "data": {
    "user": {
      "id": 1,
      "email": "iamyxn12@gmail.com",
      "role": "admin",
      "is_active": true,
      "username": "admin"
    },
    "access_token": "eyJ0eXAi...",
    "refresh_token": "eyJ0eXAi..."
  }
}
```

---

## ✅ Complete Production Checklist

- [ ] **FLASK_ENV = "production"** (not "development")
- [ ] **FLASK_DEBUG = False**
- [ ] **SECRET_KEY** = strong random value (32+ chars)
- [ ] **JWT_SECRET_KEY** = strong random value (32+ chars)
- [ ] **DATABASE_URL** = correct Supabase connection string
- [ ] **ADMIN_EMAIL** = iamyxn12@gmail.com
- [ ] **ADMIN_PASSWORD** = admin123
- [ ] **ADMIN_USERNAME** = admin
- [ ] **FRONTEND_URL** = your actual frontend domain (for CORS)
- [ ] **App restarted** after setting env vars
- [ ] **Tested login** with curl or Postman

---

## 🔍 Debugging in Production

If still getting 401 after setting env vars:

### 1. Check if variables are loaded:
```bash
# In your deployment logs, look for:
# "Database URI: postgresql+psycopg://..."
# This confirms DATABASE_URL is set
```

### 2. Check app logs:
```bash
# Vercel: Check "Logs" in your deployment
# Railway: Check "Deployment" logs
# Render: Check "Logs" tab
# Look for error messages related to database or authentication
```

### 3. Verify admin user exists:
If you can SSH to server:
```bash
python fix_production_login.py
```

### 4. Common Error Messages:
- **"Invalid email or password"** → Admin user doesn't exist or password wrong
- **"User not found or inactive"** → Admin exists but is_active = False
- **"Authentication required"** → JWT_SECRET_KEY mismatch

---

## 📝 Quick Reference

| Env Var | Local | Production | Notes |
|---------|-------|------------|-------|
| FLASK_ENV | development | **production** | ⚠️ Must be "production" |
| FLASK_DEBUG | True | **False** | ⚠️ Never True in production |
| SECRET_KEY | placeholder | **strong value** | ⚠️ Use secrets.token_hex(32) |
| JWT_SECRET_KEY | placeholder | **strong value** | ⚠️ Critical for tokens |
| DATABASE_URL | localhost | **Supabase URL** | Must match where admin exists |
| FRONTEND_URL | localhost:5173 | **your domain** | For CORS headers |

---

## 💡 Pro Tips

1. **Never commit `.env` to git** - Use `.env.example` for template
2. **Use different keys for local vs production** - Ensure security
3. **Test in staging before production** - Catch issues early
4. **Keep admin password strong** - Don't use "admin123" forever
5. **Monitor logs regularly** - Catch authentication issues fast

---

**Still having issues?** Share your:
1. Hosting platform (Vercel/Railway/etc)
2. Error message from production logs
3. Which env vars are actually set in production
