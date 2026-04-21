"""
Quick Test: Verify login works end-to-end
"""
import json
from app import create_app

app = create_app()
client = app.test_client()

print("\n" + "="*70)
print("🧪 TESTING LOGIN ENDPOINT")
print("="*70)

# Test with correct credentials
print("\n📝 Test 1: Login with CORRECT credentials")
print("   Email: iamyxn12@gmail.com")
print("   Password: admin123")

response = client.post(
    '/api/auth/login',
    data=json.dumps({
        'email': 'iamyxn12@gmail.com',
        'password': 'admin123'
    }),
    content_type='application/json'
)

print(f"\n   Status: {response.status_code}")
data = response.get_json()

if response.status_code == 200:
    print("   ✅ SUCCESS!")
    print(f"   User: {data['data']['user']['email']}")
    print(f"   Role: {data['data']['user']['role']}")
    print(f"   Token received: {'access_token' in data['data']}")
else:
    print(f"   ❌ FAILED!")
    print(f"   Error: {data.get('message', 'Unknown error')}")

# Test with wrong password
print("\n\n📝 Test 2: Login with WRONG password")
print("   Email: iamyxn12@gmail.com")
print("   Password: wrongpassword")

response2 = client.post(
    '/api/auth/login',
    data=json.dumps({
        'email': 'iamyxn12@gmail.com',
        'password': 'wrongpassword'
    }),
    content_type='application/json'
)

print(f"\n   Status: {response2.status_code}")
data2 = response2.get_json()
print(f"   Message: {data2.get('message', 'Unknown error')}")

if response2.status_code == 401:
    print("   ✅ Correctly rejected")
else:
    print("   ❌ Should return 401")

print("\n" + "="*70)

# Summary
print("\n✨ SUMMARY:")
if response.status_code == 200:
    print("   ✅ Your login endpoint is working correctly!")
    print("   ✅ Admin user exists and password is valid")
    print("\n   If you're still getting 401 in production:")
    print("   1. Check your production environment variables are set")
    print("   2. Restart your production app after setting vars")
    print("   3. Make sure FRONTEND_URL is correct for CORS")
else:
    print("   ❌ Login is not working. Check admin user status:")
    print("   Run: python check_admin.py")

print("\n" + "="*70 + "\n")
