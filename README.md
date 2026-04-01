# SANA Sarees — Flask Backend API

REST API backend for the SANA Sarees & Ladies Collections web app.
Built with **Flask + PostgreSQL + JWT + WhatsApp Cloud API**.

---

## 📁 Project Structure

```
sana-backend/
├── run.py                        # Entry point
├── requirements.txt
├── .env.example                  # Copy to .env and fill in values
├── .gitignore
├── config/
│   └── settings.py               # Dev / Prod / Test config classes
├── app/
│   ├── __init__.py               # App factory (create_app)
│   ├── models/
│   │   ├── user.py               # User (JWT, bcrypt, roles)
│   │   ├── product.py            # Product
│   │   └── order.py              # Order + OrderItem
│   ├── controllers/
│   │   ├── auth_controller.py    # register, login, profile
│   │   ├── product_controller.py # CRUD + filters + image upload
│   │   ├── order_controller.py   # place order, track, admin manage
│   │   └── admin_controller.py   # dashboard stats, user management
│   ├── routes/
│   │   ├── auth_routes.py        # /api/auth/*
│   │   ├── product_routes.py     # /api/products/*
│   │   ├── order_routes.py       # /api/orders/*
│   │   ├── admin_routes.py       # /api/admin/*
│   │   ├── upload_routes.py      # /api/upload/*
│   │   └── whatsapp_routes.py    # /api/whatsapp/*
│   ├── middleware/
│   │   └── auth_middleware.py    # @jwt_required_custom, @admin_required
│   └── utils/
│       ├── helpers.py            # response helpers, file upload, pagination
│       └── whatsapp.py           # WhatsApp Cloud API service
├── migrations/                   # Flask-Migrate auto-generated
└── tests/
    ├── test_auth.py
    ├── test_products.py
    └── test_orders.py
```

---

## 🚀 Quick Start

### 1. Clone & create virtual environment
```bash
git clone <repo>
cd sana-backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure environment
```bash
cp .env.example .env
# Edit .env and set your DATABASE_URL, JWT_SECRET_KEY, etc.
```

### 4. Create PostgreSQL database
```sql
CREATE DATABASE sana_db;
```

### 5. Run database migrations
```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### 6. Start the server
```bash
python run.py
# API available at http://localhost:5000
```

---

## 🔑 Default Admin Credentials
```
Username: admin
Password: admin123
```
> Change these in your `.env` before deploying to production!

---

## 📡 API Endpoints

### Auth  `/api/auth`
| Method | Endpoint          | Auth     | Description           |
|--------|-------------------|----------|-----------------------|
| POST   | /register         | Public   | Create customer account |
| POST   | /login            | Public   | Customer login        |
| POST   | /admin/login      | Public   | Admin login           |
| POST   | /refresh          | JWT      | Refresh access token  |
| GET    | /me               | JWT      | Get own profile       |
| PATCH  | /me               | JWT      | Update own profile    |

### Products  `/api/products`
| Method | Endpoint          | Auth     | Description           |
|--------|-------------------|----------|-----------------------|
| GET    | /                 | Public   | List products (filters, pagination, sort) |
| GET    | /filters          | Public   | Get distinct filter values |
| GET    | /:id              | Public   | Get single product    |
| POST   | /                 | Admin    | Create product        |
| PUT    | /:id              | Admin    | Update product        |
| DELETE | /:id              | Admin    | Soft-delete product   |

**Query params for GET /api/products:**
`?occasion=Wedding&fabric=Silk&min_price=1000&max_price=20000&in_stock=true&is_new=true&sort=price_asc&search=kanchi&page=1&per_page=12`

### Orders  `/api/orders`
| Method | Endpoint              | Auth     | Description            |
|--------|-----------------------|----------|------------------------|
| POST   | /                     | Public   | Place an order (auto-notifies admin on WhatsApp) |
| GET    | /track/:order_number  | Public   | Track order by number  |
| GET    | /my                   | JWT      | My order history       |
| GET    | /                     | Admin    | All orders             |
| PATCH  | /:id/status           | Admin    | Update order status    |
| DELETE | /:id                  | Admin    | Delete order           |

### Admin  `/api/admin`
| Method | Endpoint              | Auth  | Description              |
|--------|-----------------------|-------|--------------------------|
| GET    | /dashboard            | Admin | Stats + recent orders    |
| GET    | /users                | Admin | List all users           |
| GET    | /users/:id            | Admin | Get user                 |
| PATCH  | /users/:id/toggle     | Admin | Activate / deactivate    |
| DELETE | /users/:id            | Admin | Delete user              |
| GET    | /products             | Admin | All products incl. inactive |
| GET    | /orders               | Admin | All orders               |

### Upload  `/api/upload`
| Method | Endpoint  | Auth  | Description            |
|--------|-----------|-------|------------------------|
| POST   | /image    | Admin | Upload product image   |
| DELETE | /image    | Admin | Delete uploaded image  |

### WhatsApp  `/api/whatsapp`
| Method | Endpoint  | Auth   | Description                  |
|--------|-----------|--------|------------------------------|
| GET    | /webhook  | Public | Meta webhook verification    |
| POST   | /webhook  | Public | Receive incoming WA messages |
| POST   | /send     | Admin  | Send manual WA message       |

### Health
| Method | Endpoint    | Description       |
|--------|-------------|-------------------|
| GET    | /api/health | API health check  |

---

## 🗄️ Database Models

### User
`id, username, email, password_hash, phone, role (customer|admin), is_active, created_at`

### Product
`id, name, description, price, original_price, discount, image_url, occasion, fabric, color, care, in_stock, is_new, is_active, created_at`

### Order
`id, order_number, user_id, customer_name, customer_phone, customer_email, customer_address, total_amount, status, notes, source (website|whatsapp), wa_notified, created_at`

### OrderItem
`id, order_id, product_id, product_name, product_image, unit_price, quantity`

---

## 🧪 Running Tests
```bash
pytest tests/ -v
```

---

## 🌐 Production Deployment
```bash
# Using Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 "run:app"

# With environment
FLASK_ENV=production gunicorn -w 4 -b 0.0.0.0:5000 "run:app"
```

---

## 🔗 Connecting to React Frontend

In your `.env`:
```
FRONTEND_URL=http://localhost:5173
```

In React (replace `http://localhost:5000` with your deployed URL):
```js
// src/services/api.js
const API_BASE = 'http://localhost:5000/api'

export const fetchProducts = () =>
  fetch(`${API_BASE}/products`).then(r => r.json())

export const placeOrder = (orderData) =>
  fetch(`${API_BASE}/orders`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(orderData),
  }).then(r => r.json())
```
