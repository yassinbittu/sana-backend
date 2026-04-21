"""
🖼️  FRONTEND IMAGE LOADING FIX GUIDE

Your backend returns RELATIVE URLs: /uploads/products/filename.jpg

But frontend needs ABSOLUTE URLs: https://backend.com/uploads/products/filename.jpg
"""

print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    🖼️  FRONTEND IMAGE FIX GUIDE                             ║
╚══════════════════════════════════════════════════════════════════════════════╝

❌ PROBLEM:
   Backend returns: /uploads/products/6b60920b05634f439169107a5ade067c.png
   Frontend uses it as: <img src="/uploads/products/6b60920b05634f439169107a5ade067c.png" />
   Result: Image doesn't load because it's looking on FRONTEND domain, not backend!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ SOLUTION:
   Prepend your BACKEND URL to make absolute URL!

   const BACKEND_URL = 'https://your-backend-domain.com';
   const imageUrl = BACKEND_URL + product.image_url;
   // Result: https://your-backend-domain.com/uploads/products/6b60920b05634f439169107a5ade067c.png

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📍 YOUR FRONTEND DOMAIN:
   https://sanasarees-olive.vercel.app
   
📍 YOUR BACKEND DOMAIN:
   https://your-backend-domain.com (you need to tell me this)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔧 FIX FOR REACT (Most Common):

Step 1: Create API configuration file (src/config/api.js)
────────────────────────────────────────────────────────────────────────────

export const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:5000';
export const IMAGE_URL = (path) => `${API_BASE_URL}${path}`;

// Usage: IMAGE_URL('/uploads/products/filename.jpg')
// Returns: 'https://your-backend.com/uploads/products/filename.jpg'


Step 2: Update your .env file (frontend)
────────────────────────────────────────────────────────────────────────────

Development:
REACT_APP_API_BASE_URL=http://localhost:5000

Production:
REACT_APP_API_BASE_URL=https://your-backend-domain.com


Step 3: Use in your product components
────────────────────────────────────────────────────────────────────────────

// ❌ WRONG:
<img src={product.image_url} alt={product.name} />

// ✅ RIGHT:
import { IMAGE_URL } from '../config/api';

<img src={IMAGE_URL(product.image_url)} alt={product.name} />

// OR inline:
<img src={`${API_BASE_URL}${product.image_url}`} alt={product.name} />


Step 4: Create a reusable ProductImage component
────────────────────────────────────────────────────────────────────────────

import { API_BASE_URL } from '../config/api';

export function ProductImage({ imageUrl, alt }) {
  const fullUrl = imageUrl ? `${API_BASE_URL}${imageUrl}` : '/placeholder.jpg';
  
  return (
    <img 
      src={fullUrl}
      alt={alt}
      onError={(e) => {
        e.target.src = '/placeholder.jpg'; // Fallback image
      }}
    />
  );
}

// Usage:
<ProductImage 
  imageUrl={product.image_url} 
  alt={product.name} 
/>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔧 FIX FOR VUE:

Step 1: Create composable (composables/useApi.js)
────────────────────────────────────────────────────────────────────────────

export function useApi() {
  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000';
  
  return {
    API_BASE_URL,
    getImageUrl: (path) => `${API_BASE_URL}${path}`
  };
}


Step 2: Update .env (frontend)
────────────────────────────────────────────────────────────────────────────

VITE_API_BASE_URL=http://localhost:5000


Step 3: Use in components
────────────────────────────────────────────────────────────────────────────

<script setup>
import { useApi } from '@/composables/useApi';

const { getImageUrl } = useApi();

defineProps({
  product: Object
});
</script>

<template>
  <img :src="getImageUrl(product.image_url)" :alt="product.name" />
</template>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🧪 TESTING IN BROWSER:

Step 1: Open your frontend page where images should show
Step 2: Press F12 to open DevTools
Step 3: Go to "Console" tab
Step 4: Paste this:

fetch('https://your-backend.com/api/products')
  .then(r => r.json())
  .then(d => {
    const product = d.data[0];
    console.log('Product:', product);
    console.log('Image URL:', product.image_url);
    console.log('Full URL:', 'https://your-backend.com' + product.image_url);
    const img = new Image();
    img.onload = () => console.log('✅ Image loads!');
    img.onerror = () => console.log('❌ Image fails to load');
    img.src = 'https://your-backend.com' + product.image_url;
  });

If "✅ Image loads!" appears, your URL is correct.
If "❌ Image fails to load" appears, check the URL.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

❓ TROUBLESHOOTING:

1. Still not working?
   • Open DevTools (F12)
   • Go to Network tab
   • Load a product page
   • Look for failed image requests
   • Check what URL it's trying to load
   • Share the URL with me

2. Getting CORS errors?
   • Backend already has CORS fix ✅
   • Make sure you updated and redeployed backend

3. Getting "Image not found"?
   • Check backend URL is correct
   • Verify image file exists in /uploads/products/

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚡ QUICK COPY-PASTE SOLUTION FOR REACT:

// In your component:
const API_URL = 'https://your-backend-domain.com'; // ← UPDATE THIS

{products.map(product => (
  <div key={product.id}>
    <img 
      src={`${API_URL}${product.image_url}`} 
      alt={product.name}
      onError={(e) => e.target.style.display = 'none'}
    />
    <h3>{product.name}</h3>
  </div>
))}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

❌ WHAT NOT TO DO:

• Don't use: <img src={product.image_url} />
• Don't use: <img src="/{product.image_url}" />
• Don't use: <img src="http://localhost:5000{product.image_url}" /> (hardcoded)

✅ WHAT TO DO:

• Use: <img src={`${API_BASE_URL}${product.image_url}`} />
• Use environment variables for backend URL
• Use the same API URL as your axios/fetch calls

╚══════════════════════════════════════════════════════════════════════════════╝
""")

print("""
📋 WHAT YOU NEED TO TELL ME:

1. What's your backend URL?
   (e.g., https://sana-api.vercel.app)

2. What frontend framework are you using?
   (React / Vue / Next.js / etc)

3. Can you share your ProductImage or Product card component?
   (So I can see exactly how you're loading images)

4. What error do you see in browser console?
   (Press F12, go to Console)

Reply with this info and I'll give you exact code to fix it!
""")
