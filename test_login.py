from app import create_app
import json

app = create_app()
client = app.test_client()

# Test login with correct credentials
print("=" * 60)
print("Testing login with email: iamyxn12@gmail.com")
print("Testing login with password: admin123")
print("=" * 60)

response = client.post(
    '/api/auth/login',
    data=json.dumps({
        'email': 'iamyxn12@gmail.com',
        'password': 'admin123'
    }),
    content_type='application/json'
)

print(f"Status Code: {response.status_code}")
print(f"Response: {response.get_json()}")

if response.status_code == 200:
    print("\n✅ Login successful!")
    data = response.get_json()
    if data.get('data') and data['data'].get('access_token'):
        print("✅ Access token generated successfully!")
else:
    print("\n❌ Login failed!")
