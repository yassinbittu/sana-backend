"""
Tests for /api/auth endpoints.
Run with:  pytest tests/ -v
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


def test_health(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json["success"] is True


def test_register(client):
    r = client.post("/api/auth/register", json={
        "username": "testuser",
        "email":    "test@example.com",
        "password": "test123",
        "phone":    "9876543210",
    })
    assert r.status_code == 201
    assert r.json["success"] is True
    assert "access_token" in r.json["data"]


def test_register_duplicate_email(client):
    client.post("/api/auth/register", json={
        "username": "user2",
        "email":    "dupe@example.com",
        "password": "test123",
    })
    r = client.post("/api/auth/register", json={
        "username": "user3",
        "email":    "dupe@example.com",
        "password": "test123",
    })
    assert r.status_code == 409


def test_login(client):
    r = client.post("/api/auth/login", json={
        "email":    "test@example.com",
        "password": "test123",
    })
    assert r.status_code == 200
    assert r.json["data"]["user"]["email"] == "test@example.com"


def test_login_wrong_password(client):
    r = client.post("/api/auth/login", json={
        "email":    "test@example.com",
        "password": "wrongpass",
    })
    assert r.status_code == 401


def test_get_profile_without_token(client):
    r = client.get("/api/auth/me")
    assert r.status_code == 401


def test_get_profile_with_token(client):
    login = client.post("/api/auth/login", json={
        "email": "test@example.com", "password": "test123"
    })
    token = login.json["data"]["access_token"]
    r = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert r.json["data"]["user"]["email"] == "test@example.com"
