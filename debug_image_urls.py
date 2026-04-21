"""
Image URL Format Test - Shows frontend exactly how to load images
"""
import json
from app import create_app
from app.models.product import Product

app = create_app()
client = app.test_client()

print("\n" + "="*80)
print("📸 IMAGE URL FORMAT TEST")
print("="*80)

with app.app_context():
    # Get a product with an image
    product = Product.query.filter(Product.image_url.isnot(None)).first()
    
    if product:
        print(f"\n✅ Found product with image: {product.name}")
        print(f"\n1️⃣  Image URL stored in database:")
        print(f"   {product.image_url}")
        
        print(f"\n2️⃣  What API returns (via GET /api/products/{product.id}):")
        response = client.get(f'/api/products/{product.id}')
        data = response.get_json()
        print(f"   Response: {data}")
        if 'data' in data and 'product' in data['data']:
            image_url = data['data']['product']['image_url']
        else:
            image_url = product.image_url
        print(f"   Image URL: {image_url}")
        
        print(f"\n3️⃣  ⚠️  HOW FRONTEND SHOULD LOAD IMAGE:")
        print("""
   The backend returns RELATIVE URLs like: /uploads/products/filename.jpg
   
   INCORRECT (won't work):
   <img src="/uploads/products/filename.jpg" />
   
   CORRECT (works):
   <img src="https://YOUR_BACKEND_URL/uploads/products/filename.jpg" />
   
   OR if your frontend is on SAME domain as backend:
   <img src={`${window.location.origin}${imageUrl}`} />
        """)
        
        print(f"\n4️⃣  Frontend Implementation Examples:")
        print("""
   REACT:
   ──────────────────────────────────────────────────────
   const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:5000';
   
   <img 
     src={`${BACKEND_URL}${product.image_url}`}
     alt={product.name}
   />
   
   OR with window.location:
   ──────────────────────────────────────────────────────
   <img 
     src={`${window.location.origin}${product.image_url}`}
     alt={product.name}
   />
   
   VUE:
   ──────────────────────────────────────────────────────
   <img 
     :src="`${backendUrl}${product.image_url}`"
     :alt="product.name"
   />
   
   PLAIN HTML/JS:
   ──────────────────────────────────────────────────────
   const BACKEND_URL = 'https://your-backend.vercel.app';
   const imageUrl = BACKEND_URL + product.image_url;
   img.src = imageUrl;
        """)
        
        print(f"\n5️⃣  Test if backend serves image correctly:")
        img_response = client.get(image_url)
        if img_response.status_code == 200:
            print(f"   ✅ Backend can serve image (HTTP 200)")
            print(f"   Content-Type: {img_response.content_type}")
            print(f"   Size: {len(img_response.data)} bytes")
        else:
            print(f"   ❌ Backend cannot serve image (HTTP {img_response.status_code})")
    
    else:
        print("\n⚠️  No products with images found in database")
        print("   Upload a product image first using admin panel")

print("\n" + "="*80)
print("✨ SUMMARY")
print("="*80)
print("""
If images are STILL not showing after this fix:

1. CHECK: Is your BACKEND_URL correct in frontend?
   - Ask: What's your backend URL?
   - Example: https://sana-backend.vercel.app
   
2. CHECK: Are you constructing image URLs correctly?
   - WRONG: <img src="/uploads/products/file.jpg" />
   - RIGHT: <img src="https://sana-backend.vercel.app/uploads/products/file.jpg" />
   
3. CHECK: Browser console for errors
   - Open DevTools (F12)
   - Go to Console tab
   - Look for "Failed to fetch" or CORS errors
   - Share the error message

4. CHECK: Network tab
   - Go to Network tab
   - Try to load a product
   - Look for failed image requests
   - Check the URL being requested
""")
print("="*80 + "\n")
