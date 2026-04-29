"""Integration tests for the restructured Media Upload API."""

import sys
from pathlib import Path
from types import SimpleNamespace
from fastapi.testclient import TestClient

# Adjust path to find src
sys.path.append(str(Path(__file__).resolve().parents[1]))
from src.api.server import app

client = TestClient(app)


def test_status_endpoint():
    """Verify health check works with new naming."""
    response = client.get("/status")
    assert response.status_code == 200
    assert response.json()["active"] is True
    assert "node" in response.json()


def test_empty_upload_fails():
    """Verify error handling for missing files."""
    # FastAPI expects a file field named 'file'
    response = client.post("/upload")
    assert response.status_code == 422 # FastAPI validation error for missing field


def test_unsupported_media_type():
    """Verify rejection of non-image files."""
    response = client.post(
        "/upload",
        files={"file": ("test.txt", b"some text", "text/plain")}
    )
    assert response.status_code == 415


def test_successful_flow(monkeypatch):
    """Verify end-to-end flow with mocks."""
    
    class MockHandler:
        def __init__(self, cfg): pass
        def process_and_store(self, data, ext, mime):
            return "cdn/uploads/mock-id.png"
        def get_signed_link(self, path):
            return f"https://s3.mock.com/{path}?token=abc"

    # Mock initialization and handler
    monkeypatch.setattr("src.api.server.initialize_config", lambda: SimpleNamespace(
        aws_key="key", aws_secret="secret", bucket="bucket", region_name="us-east-1"
    ))
    monkeypatch.setattr("src.api.server.ImageStorageHandler", MockHandler)

    response = client.post(
        "/upload",
        files={"file": ("image.png", b"fake-data", "image/png")}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "link" in data["data"]
    assert "mock-id.png" in data["data"]["ref"]


def test_oversized_file():
    """Verify rejection of files > 2MB."""
    huge_data = b"x" * (2 * 1024 * 1024 + 100)
    response = client.post(
        "/upload",
        files={"file": ("large.jpg", huge_data, "image/jpeg")}
    )
    assert response.status_code == 413
