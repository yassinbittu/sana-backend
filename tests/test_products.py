"""
Tests for /api/products endpoints.
"""
import pytest
from app import create_app, db
from config.settings import TestingConfig


@pytest.fixture(scope="module")
def client():
    app = create_app(TestingConfig)
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.drop_all()


def _admin_token(client):
    r = client.post("/api/auth/admin/login", json={
        "username": "admin", "password": "admin123"
    })
    return r.json["data"]["access_token"]


def test_get_products_empty(client):
    r = client.get("/api/products")
    assert r.status_code == 200
    assert r.json["success"] is True
    assert isinstance(r.json["data"], list)


def test_create_product_no_auth(client):
    r = client.post("/api/products", json={"name": "Test", "price": 999})
    assert r.status_code == 401


def test_create_product_admin(client):
    token = _admin_token(client)
    r = client.post("/api/products",
        json={
            "name":     "Kanjivaram Silk Saree",
            "price":    12500,
            "occasion": "Wedding",
            "fabric":   "Pure Silk",
            "in_stock": True,
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 201
    assert r.json["data"]["product"]["name"] == "Kanjivaram Silk Saree"


def test_get_product_by_id(client):
    token = _admin_token(client)
    create = client.post("/api/products",
        json={"name": "Chiffon Saree", "price": 3499},
        headers={"Authorization": f"Bearer {token}"},
    )
    pid = create.json["data"]["product"]["id"]
    r   = client.get(f"/api/products/{pid}")
    assert r.status_code == 200


def test_update_product(client):
    token = _admin_token(client)
    create = client.post("/api/products",
        json={"name": "Old Name", "price": 5000},
        headers={"Authorization": f"Bearer {token}"},
    )
    pid = create.json["data"]["product"]["id"]
    r = client.put(f"/api/products/{pid}",
        json={"name": "New Name", "price": 4500},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200
    assert r.json["data"]["product"]["name"] == "New Name"


def test_delete_product(client):
    token = _admin_token(client)
    create = client.post("/api/products",
        json={"name": "To Delete", "price": 1000},
        headers={"Authorization": f"Bearer {token}"},
    )
    pid = create.json["data"]["product"]["id"]
    r = client.delete(f"/api/products/{pid}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200
    # Should be soft-deleted (not found publicly)
    r2 = client.get(f"/api/products/{pid}")
    assert r2.status_code == 404
