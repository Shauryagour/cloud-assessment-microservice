"""Automated test suite for Cloud Assessment Microservice.

Includes at least 4 test cases (total: 8) covering:
1. Health check endpoint
2. Root metadata endpoint
3. System info endpoint
4. Listing items
5. Creating items (happy path)
6. Data validation rejection (error path)
7. Fetching specific item & 404 handling
8. Item deletion & 404 handling
"""
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    """Test 1: Health check endpoint returns status 200 and healthy status."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "cloud-assessment-microservice"
    assert "uptime_seconds" in data
    assert data["uptime_seconds"] >= 0


def test_root_endpoint():
    """Test 2: Root endpoint returns service metadata and navigation."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "service" in data
    assert "documentation" in data
    assert "endpoints" in data


def test_system_info_endpoint():
    """Test 3: System info endpoint exposes container runtime info."""
    response = client.get("/api/info")
    assert response.status_code == 200
    data = response.json()
    assert "hostname" in data
    assert "platform" in data
    assert "python_version" in data
    assert "environment" in data


def test_list_items():
    """Test 4: List items endpoint returns pre-seeded collection."""
    response = client.get("/api/items")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 3


def test_create_item_success():
    """Test 5: Create item succeeds with 201 status code and assigned ID."""
    payload = {
        "title": "Configure Prometheus metrics",
        "description": "Expose metrics for cloud monitoring.",
        "status": "pending",
        "priority": "high",
    }
    response = client.post("/api/items", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["id"] > 3
    assert data["title"] == payload["title"]
    assert data["status"] == "pending"
    assert "created_at" in data


def test_create_item_validation_error():
    """Test 6: Reject invalid payload with HTTP 422 Unprocessable Entity."""
    # Missing required field 'title'
    invalid_payload = {
        "description": "Missing title",
        "status": "pending",
    }
    response = client.post("/api/items", json=invalid_payload)
    assert response.status_code == 422


def test_get_item_by_id_and_not_found():
    """Test 7: Fetch existing item returns 200; non-existent ID returns 404."""
    # Existing item
    res_ok = client.get("/api/items/1")
    assert res_ok.status_code == 200
    assert res_ok.json()["id"] == 1

    # Non-existent item
    res_404 = client.get("/api/items/99999")
    assert res_404.status_code == 404
    assert "detail" in res_404.json()


def test_delete_item_success_and_not_found():
    """Test 8: Delete item returns 200 and subsequent fetch returns 404."""
    # Create an item first to delete
    create_res = client.post("/api/items", json={"title": "Temporary Item"})
    assert create_res.status_code == 201
    item_id = create_res.json()["id"]

    # Delete it
    del_res = client.delete(f"/api/items/{item_id}")
    assert del_res.status_code == 200

    # Verify it is gone
    get_res = client.get(f"/api/items/{item_id}")
    assert get_res.status_code == 404
