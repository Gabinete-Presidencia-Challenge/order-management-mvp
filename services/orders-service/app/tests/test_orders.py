import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
#from unittest.mock import patch
from unittest.mock import patch

from app.main import app
from app.db.session import get_db
from app.models.order import Base, OrderStatus

# In-memory SQLite for testing (schema compatible subset)
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_orders.db"

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


ORDER_PAYLOAD = {
    "customer_name": "Alice Smith",
    "customer_email": "alice@example.com",
    "notes": "Please handle with care",
    "items": [
        {"product_name": "Widget A", "product_sku": "SKU-001", "quantity": 2, "unit_price": 29.99},
        {"product_name": "Widget B", "product_sku": "SKU-002", "quantity": 1, "unit_price": 49.99},
    ],
}


class TestHealthEndpoint:
    def test_health_returns_ok(self):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"
        assert response.json()["service"] == "orders-service"


class TestCreateOrder:
    def test_create_order_success(self):
        response = client.post("/api/v1/orders", json=ORDER_PAYLOAD)
        assert response.status_code == 201
        data = response.json()
        assert data["customer_name"] == "Alice Smith"
        assert data["customer_email"] == "alice@example.com"
        assert data["status"] == OrderStatus.PENDING
        assert len(data["items"]) == 2
        assert abs(data["total_amount"] - 109.97) < 0.01

    def test_create_order_computes_total(self):
        response = client.post("/api/v1/orders", json=ORDER_PAYLOAD)
        data = response.json()
        expected = 2 * 29.99 + 1 * 49.99
        assert abs(data["total_amount"] - expected) < 0.01

    def test_create_order_without_items_fails(self):
        payload = {**ORDER_PAYLOAD, "items": []}
        response = client.post("/api/v1/orders", json=payload)
        assert response.status_code == 422

    def test_create_order_invalid_email_fails(self):
        payload = {**ORDER_PAYLOAD, "customer_email": "not-an-email"}
        response = client.post("/api/v1/orders", json=payload)
        assert response.status_code == 422

    def test_create_order_has_pending_status(self):
        response = client.post("/api/v1/orders", json=ORDER_PAYLOAD)
        assert response.json()["status"] == "pending"

    def test_create_order_records_status_history(self):
        response = client.post("/api/v1/orders", json=ORDER_PAYLOAD)
        data = response.json()
        assert len(data["status_history"]) == 1
        assert data["status_history"][0]["new_status"] == "pending"


class TestGetOrder:
    def test_get_existing_order(self):
        create_resp = client.post("/api/v1/orders", json=ORDER_PAYLOAD)
        order_id = create_resp.json()["id"]

        response = client.get(f"/api/v1/orders/{order_id}")
        assert response.status_code == 200
        assert response.json()["id"] == order_id

    def test_get_nonexistent_order_returns_404(self):
        response = client.get("/api/v1/orders/00000000-0000-0000-0000-000000000000")
        assert response.status_code == 404

    def test_get_order_includes_items(self):
        create_resp = client.post("/api/v1/orders", json=ORDER_PAYLOAD)
        order_id = create_resp.json()["id"]

        response = client.get(f"/api/v1/orders/{order_id}")
        assert len(response.json()["items"]) == 2


class TestListOrders:
    def test_list_orders_empty(self):
        response = client.get("/api/v1/orders")
        assert response.status_code == 200
        assert response.json()["total"] == 0
        assert response.json()["items"] == []

    def test_list_orders_returns_created_orders(self):
        client.post("/api/v1/orders", json=ORDER_PAYLOAD)
        client.post("/api/v1/orders", json=ORDER_PAYLOAD)

        response = client.get("/api/v1/orders")
        assert response.json()["total"] == 2

    def test_list_orders_filter_by_status(self):
        client.post("/api/v1/orders", json=ORDER_PAYLOAD)

        response = client.get("/api/v1/orders?status=pending")
        assert response.json()["total"] == 1

        response = client.get("/api/v1/orders?status=shipped")
        assert response.json()["total"] == 0

    def test_list_orders_pagination(self):
        for _ in range(5):
            client.post("/api/v1/orders", json=ORDER_PAYLOAD)

        response = client.get("/api/v1/orders?page=1&page_size=3")
        data = response.json()
        assert data["total"] == 5
        assert len(data["items"]) == 3

        response = client.get("/api/v1/orders?page=2&page_size=3")
        assert len(response.json()["items"]) == 2


class TestUpdateOrderStatus:
    def test_update_status_success(self):
        create_resp = client.post("/api/v1/orders", json=ORDER_PAYLOAD)
        order_id = create_resp.json()["id"]

        response = client.patch(
            f"/api/v1/orders/{order_id}/status",
            json={"status": "confirmed", "changed_by": "operator@test.com"},
        )
        assert response.status_code == 200
        assert response.json()["status"] == "confirmed"

    def test_update_status_records_history(self):
        create_resp = client.post("/api/v1/orders", json=ORDER_PAYLOAD)
        order_id = create_resp.json()["id"]

        client.patch(f"/api/v1/orders/{order_id}/status", json={"status": "confirmed"})
        client.patch(f"/api/v1/orders/{order_id}/status", json={"status": "processing"})

        response = client.get(f"/api/v1/orders/{order_id}")
        history = response.json()["status_history"]
        assert len(history) == 3  # pending, confirmed, processing

    def test_update_status_nonexistent_order_returns_404(self):
        response = client.patch(
            "/api/v1/orders/00000000-0000-0000-0000-000000000000/status",
            json={"status": "confirmed"},
        )
        assert response.status_code == 404

    def test_update_status_invalid_value_returns_422(self):
        create_resp = client.post("/api/v1/orders", json=ORDER_PAYLOAD)
        order_id = create_resp.json()["id"]
        response = client.patch(
            f"/api/v1/orders/{order_id}/status",
            json={"status": "invalid_status"},
        )
        assert response.status_code == 422


class TestDeleteOrder:
    def test_delete_order_success(self):
        create_resp = client.post("/api/v1/orders", json=ORDER_PAYLOAD)
        order_id = create_resp.json()["id"]

        response = client.delete(f"/api/v1/orders/{order_id}")
        assert response.status_code == 204

        get_resp = client.get(f"/api/v1/orders/{order_id}")
        assert get_resp.status_code == 404

    def test_delete_nonexistent_order_returns_404(self):
        response = client.delete("/api/v1/orders/00000000-0000-0000-0000-000000000000")
        assert response.status_code == 404
