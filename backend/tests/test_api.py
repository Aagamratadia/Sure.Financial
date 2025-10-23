"""Basic tests for the API"""
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data


def test_health_check():
    """Test health endpoint"""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "services" in data


def test_upload_no_file():
    """Test upload without file"""
    response = client.post("/api/v1/parse/upload")
    assert response.status_code == 422  # Validation error


def test_batch_no_files():
    """Test batch upload without files"""
    response = client.post("/api/v1/parse/batch")
    assert response.status_code == 422


def test_get_nonexistent_job():
    """Test getting status of nonexistent job"""
    response = client.get("/api/v1/parse/fake-job-id/status")
    assert response.status_code in [404, 500]  # Depends on MongoDB connection
