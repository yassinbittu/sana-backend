"""
Tests for /api/orders endpoints.
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


def _create_product(client, token):
    r = client.post("/api/products",
        json={"name": "Test Saree", "price": 5000, "in_stock": True},
        headers={"Authorization": f"Bearer {token}"},
    )
    return r.json["data"]["product"]["id"]


def test_create_order_guest(client):
    token = _admin_token(client)
    pid   = _create_product(client, token)

    r = client.post("/api/orders", json={
        "customer_name":  "Priya Sharma",
        "customer_phone": "9876543210",
        "items": [{"product_id": pid, "quantity": 1}],
    })
    assert r.status_code == 201
    assert r.json["success"] is True
    assert r.json["data"]["order"]["customer_name"] == "Priya Sharma"
    assert r.json["data"]["order"]["order_number"].startswith("SANA-")


def test_create_order_missing_fields(client):
    r = client.post("/api/orders", json={"customer_name": "Test"})
    assert r.status_code == 400


def test_track_order(client):
    token = _admin_token(client)
    pid   = _create_product(client, token)

    create = client.post("/api/orders", json={
        "customer_name":  "Lakshmi",
        "customer_phone": "9876500001",
        "items": [{"product_id": pid, "quantity": 2}],
    })
    order_number = create.json["data"]["order"]["order_number"]

    r = client.get(f"/api/orders/track/{order_number}")
    assert r.status_code == 200
    assert r.json["data"]["order"]["order_number"] == order_number


def test_update_order_status(client):
    token = _admin_token(client)
    pid   = _create_product(client, token)

    create = client.post("/api/orders", json={
        "customer_name":  "Anita",
        "customer_phone": "9876500002",
        "items": [{"product_id": pid, "quantity": 1}],
    })
    oid = create.json["data"]["order"]["id"]

    r = client.patch(f"/api/orders/{oid}/status",
        json={"status": "confirmed"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200
    assert r.json["data"]["order"]["status"] == "confirmed"


def test_invalid_status(client):
    token = _admin_token(client)
    pid   = _create_product(client, token)

    create = client.post("/api/orders", json={
        "customer_name":  "Rekha",
        "customer_phone": "9876500003",
        "items": [{"product_id": pid, "quantity": 1}],
    })
    oid = create.json["data"]["order"]["id"]

    r = client.patch(f"/api/orders/{oid}/status",
        json={"status": "flying"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 400
