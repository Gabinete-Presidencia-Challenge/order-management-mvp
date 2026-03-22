import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db.session import get_db
from app.models.user import Base

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_users.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

USER_PAYLOAD = {
    "email": "bob@example.com",
    "full_name": "Bob Jones",
    "password": "SecurePass123!",
    "role": "operator",
}


class TestHealthEndpoint:
    def test_health_returns_ok(self):
        r = client.get("/health")
        assert r.status_code == 200
        assert r.json()["service"] == "users-service"


class TestRegister:
    def test_register_success(self):
        r = client.post("/api/v1/auth/register", json=USER_PAYLOAD)
        assert r.status_code == 201
        data = r.json()
        assert data["email"] == USER_PAYLOAD["email"]
        assert data["full_name"] == USER_PAYLOAD["full_name"]
        assert "hashed_password" not in data

    def test_register_duplicate_email_returns_409(self):
        client.post("/api/v1/auth/register", json=USER_PAYLOAD)
        r = client.post("/api/v1/auth/register", json=USER_PAYLOAD)
        assert r.status_code == 409

    def test_register_invalid_email_returns_422(self):
        payload = {**USER_PAYLOAD, "email": "not-valid"}
        r = client.post("/api/v1/auth/register", json=payload)
        assert r.status_code == 422

    def test_register_default_role_is_operator(self):
        payload = {k: v for k, v in USER_PAYLOAD.items() if k != "role"}
        r = client.post("/api/v1/auth/register", json=payload)
        assert r.json()["role"] == "operator"


class TestLogin:
    def test_login_success(self):
        client.post("/api/v1/auth/register", json=USER_PAYLOAD)
        r = client.post("/api/v1/auth/login", json={
            "email": USER_PAYLOAD["email"],
            "password": USER_PAYLOAD["password"],
        })
        assert r.status_code == 200
        data = r.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["email"] == USER_PAYLOAD["email"]

    def test_login_wrong_password_returns_401(self):
        client.post("/api/v1/auth/register", json=USER_PAYLOAD)
        r = client.post("/api/v1/auth/login", json={
            "email": USER_PAYLOAD["email"],
            "password": "WrongPassword!",
        })
        assert r.status_code == 401

    def test_login_nonexistent_user_returns_401(self):
        r = client.post("/api/v1/auth/login", json={
            "email": "ghost@example.com",
            "password": "anything",
        })
        assert r.status_code == 401

    def test_login_inactive_user_returns_403(self):
        client.post("/api/v1/auth/register", json=USER_PAYLOAD)
        # Find the user and deactivate
        users_r = client.get("/api/v1/users")
        user_id = users_r.json()[0]["id"]
        client.patch(f"/api/v1/users/{user_id}", json={"is_active": False})

        r = client.post("/api/v1/auth/login", json={
            "email": USER_PAYLOAD["email"],
            "password": USER_PAYLOAD["password"],
        })
        assert r.status_code == 403


class TestUsersCRUD:
    def test_list_users_empty(self):
        r = client.get("/api/v1/users")
        assert r.status_code == 200
        assert r.json() == []

    def test_create_user(self):
        r = client.post("/api/v1/users", json=USER_PAYLOAD)
        assert r.status_code == 201
        assert r.json()["email"] == USER_PAYLOAD["email"]

    def test_create_duplicate_user_returns_409(self):
        client.post("/api/v1/users", json=USER_PAYLOAD)
        r = client.post("/api/v1/users", json=USER_PAYLOAD)
        assert r.status_code == 409

    def test_get_user_by_id(self):
        created = client.post("/api/v1/users", json=USER_PAYLOAD).json()
        r = client.get(f"/api/v1/users/{created['id']}")
        assert r.status_code == 200
        assert r.json()["id"] == created["id"]

    def test_get_nonexistent_user_returns_404(self):
        r = client.get("/api/v1/users/00000000-0000-0000-0000-000000000000")
        assert r.status_code == 404

    def test_update_user_full_name(self):
        created = client.post("/api/v1/users", json=USER_PAYLOAD).json()
        r = client.patch(f"/api/v1/users/{created['id']}", json={"full_name": "Bob Updated"})
        assert r.status_code == 200
        assert r.json()["full_name"] == "Bob Updated"

    def test_update_user_role(self):
        created = client.post("/api/v1/users", json=USER_PAYLOAD).json()
        r = client.patch(f"/api/v1/users/{created['id']}", json={"role": "admin"})
        assert r.json()["role"] == "admin"

    def test_delete_user(self):
        created = client.post("/api/v1/users", json=USER_PAYLOAD).json()
        r = client.delete(f"/api/v1/users/{created['id']}")
        assert r.status_code == 204
        r2 = client.get(f"/api/v1/users/{created['id']}")
        assert r2.status_code == 404

    def test_delete_nonexistent_user_returns_404(self):
        r = client.delete("/api/v1/users/00000000-0000-0000-0000-000000000000")
        assert r.status_code == 404
