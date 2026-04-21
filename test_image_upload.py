"""
Test Image Upload and Display
Verifies that images are uploaded and can be served correctly
"""
import os
import json
from io import BytesIO
from PIL import Image
from app import create_app

app = create_app()
client = app.test_client()

print("\n" + "="*70)
print("🖼️  IMAGE UPLOAD & DISPLAY TEST")
print("="*70)

# First, get admin token
print("\n1️⃣  Getting admin token...")
login_response = client.post(
    '/api/auth/login',
    data=json.dumps({
        'email': 'iamyxn12@gmail.com',
        'password': 'admin123'
    }),
    content_type='application/json'
)

if login_response.status_code != 200:
    print("❌ Failed to login admin")
    exit(1)

token = login_response.get_json()['data']['access_token']
print(f"✅ Token obtained: {token[:30]}...")

# Create a test image
print("\n2️⃣  Creating test image...")
img = Image.new('RGB', (100, 100), color='red')
img_bytes = BytesIO()
img.save(img_bytes, format='PNG')
img_bytes.seek(0)

# Upload image
print("3️⃣  Uploading image to /api/upload/image...")
upload_response = client.post(
    '/api/upload/image?folder=products',
    data={'file': (img_bytes, 'test_image.png')},
    headers={'Authorization': token}  # No "Bearer " prefix
)

print(f"   Status: {upload_response.status_code}")
upload_data = upload_response.get_json()

if upload_response.status_code != 201:
    print(f"❌ Upload failed: {upload_data}")
    exit(1)

image_url = upload_data['data']['url']
print(f"✅ Image uploaded: {image_url}")

# Test serving the image
print(f"\n4️⃣  Testing image served from: {image_url}...")
image_response = client.get(image_url)

print(f"   Status: {image_response.status_code}")
if image_response.status_code == 200:
    print(f"   Content-Type: {image_response.content_type}")
    print(f"   Content-Length: {len(image_response.data)} bytes")
    print("✅ Image served successfully!")
else:
    print(f"❌ Failed to serve image: {image_response.status_code}")
    exit(1)

# Test CORS headers
print("\n5️⃣  Checking CORS headers...")
cors_response = client.options(image_url)
cors_headers = {k: v for k, v in cors_response.headers if 'Access-Control' in k}

if cors_headers:
    print("✅ CORS headers present:")
    for header, value in cors_headers.items():
        print(f"   {header}: {value}")
else:
    print("⚠️  No CORS headers found (but images might still work)")

print("\n" + "="*70)
print("✨ IMAGE UPLOAD/DISPLAY TEST COMPLETE")
print("="*70)
print("""
✅ All tests passed! Images should now display correctly.

Next steps:
1. Push code changes to GitHub
2. Redeploy your backend (Vercel/Render/Railway)
3. Upload a new product image through admin
4. Check if image displays on frontend

Image URL format: /uploads/products/uuid.jpg
Full URL: https://your-backend.com/uploads/products/uuid.jpg
""")
print("="*70 + "\n")
