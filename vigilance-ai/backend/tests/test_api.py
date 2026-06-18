"""
VigilanceAI — API Test Suite
Run from vigilance-ai/ directory: python3 -m pytest backend/tests/ -v
"""

import sys
import numpy as np
import cv2
import pytest
import io
from pathlib import Path
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "core"))

from db.database import init_db, Base, engine
from main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def make_test_image() -> bytes:
    img = np.full((480, 640, 3), 150, dtype=np.uint8)
    cv2.rectangle(img, (100, 150), (400, 350), (200, 200, 200), -1)
    cv2.rectangle(img, (200, 320), (300, 345), (255, 255, 255), -1)
    _, buf = cv2.imencode(".jpg", img)
    return buf.tobytes()


class TestRoot:

    def test_root(self):
        resp = client.get("/")
        assert resp.status_code == 200
        assert resp.json()["system"] == "VigilanceAI"

    def test_health(self):
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "healthy"


class TestAnalyze:

    def test_analyze_valid_image(self):
        img_bytes = make_test_image()
        resp = client.post(
            "/api/v1/analyze",
            files={"file": ("test.jpg", img_bytes, "image/jpeg")},
            data={"camera_id": "CAM-001", "location": "MG Road, Bengaluru"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert "incident_id" in data
        assert "annotated_image_b64" in data
        assert "metadata" in data

    def test_analyze_returns_metadata_keys(self):
        img_bytes = make_test_image()
        resp = client.post(
            "/api/v1/analyze",
            files={"file": ("test.jpg", img_bytes, "image/jpeg")},
            data={},
        )
        assert resp.status_code == 200
        meta = resp.json()["metadata"]
        for key in ["incident_id", "timestamp", "camera_id",
                    "violations", "violation_count"]:
            assert key in meta

    def test_analyze_invalid_file(self):
        resp = client.post(
            "/api/v1/analyze",
            files={"file": ("test.txt", b"not an image", "text/plain")},
            data={},
        )
        assert resp.status_code == 400


class TestViolations:

    def test_get_violations_empty(self):
        resp = client.get("/api/v1/violations")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_get_violations_after_analyze(self):
        img_bytes = make_test_image()
        client.post(
            "/api/v1/analyze",
            files={"file": ("test.jpg", img_bytes, "image/jpeg")},
            data={},
        )
        resp = client.get("/api/v1/violations")
        assert resp.status_code == 200

    def test_get_violation_not_found(self):
        resp = client.get("/api/v1/violations/NONEXISTENT")
        assert resp.status_code == 404


class TestStats:

    def test_get_stats(self):
        resp = client.get("/api/v1/stats")
        assert resp.status_code == 200
        data = resp.json()
        assert "total_violations" in data
        assert "violations_by_type" in data
        assert "violations_by_severity" in data

    def test_get_daily_stats(self):
        resp = client.get("/api/v1/stats/daily")
        assert resp.status_code == 200
        assert "daily" in resp.json()

    def test_get_camera_stats(self):
        resp = client.get("/api/v1/stats/cameras")
        assert resp.status_code == 200
        assert "cameras" in resp.json()


class TestChallan:

    def test_get_challans_empty(self):
        resp = client.get("/api/v1/challans")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_challan_not_found(self):
        resp = client.post("/api/v1/challan/NONEXISTENT")
        assert resp.status_code == 404

    def test_challan_summary(self):
        resp = client.get("/api/v1/challans/summary")
        assert resp.status_code == 200
        data = resp.json()
        assert "total_challans" in data
        assert "total_issued_inr" in data
