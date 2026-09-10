# TechScale: Test suite

from fastapi.testclient import TestClient
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import app  # noqa: E402
import order_service  # noqa: E402

client = TestClient(app)


# Pre-written — use this as a reference before writing your own tests below.
def test_health_returns_200():
    response = client.get("/health")
    assert response.status_code == 200


# TODO: Check that the health endpoint returns a body with the expected fields.
def test_health_response_body():
    response = client.get("/health")
    assert response.json() == {"status": "healthy", "version": "1.0.0"}


# TODO: Check that the process endpoint accepts a valid payload and returns the expected status.
def test_process_returns_202():
    response = client.post("/process", json={"user_id": 42, "action": "sync"})
    assert response.status_code == 202
    assert response.json()["message"] == "Processing action sync for user 42"


# TODO: Call validate_order() directly with a valid quantity and assert it returns True.
# No database or HTTP call needed — this is a pure business logic test.
def test_validate_order_accepts_valid_quantity():
    assert order_service.validate_order(5) is True


# TODO: Call validate_order() with an out-of-range quantity and assert it raises the correct error.
def test_validate_order_rejects_invalid_quantity():
    import pytest

    with pytest.raises(ValueError, match="Quantity must be positive"):
        order_service.validate_order(0)
