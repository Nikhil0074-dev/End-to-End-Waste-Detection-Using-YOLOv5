import base64
import io

import pytest
from PIL import Image

from app import create_app


@pytest.fixture
def app():
    return create_app({"TESTING": True, "MAX_CONTENT_LENGTH": 1024 * 1024})


@pytest.fixture
def client(app):
    return app.test_client()


def png_base64():
    stream = io.BytesIO()
    Image.new("RGB", (4, 4), color="green").save(stream, format="PNG")
    return base64.b64encode(stream.getvalue()).decode("ascii")


def test_pages_load(client):
    assert client.get("/").status_code == 200
    assert client.get("/live").status_code == 200


def test_health_reports_model_unavailable(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json["status"] == "ok"


def test_predict_rejects_missing_image(client):
    response = client.post("/predict", json={})
    assert response.status_code == 400


def test_predict_rejects_invalid_json(client):
    response = client.post("/predict", data="bad", content_type="application/json")
    assert response.status_code == 400


def test_predict_returns_503_when_model_missing(client, monkeypatch):
    def unavailable(_image):
        raise FileNotFoundError("not configured")
    monkeypatch.setattr("app.detect", unavailable)
    response = client.post("/predict", json={"image": png_base64()})
    assert response.status_code == 503


def test_predict_returns_annotated_image(client, monkeypatch):
    output = b"annotated-png"
    monkeypatch.setattr("app.detect", lambda _image: output)
    response = client.post("/predict", json={"image": png_base64()})
    assert response.status_code == 200
    assert base64.b64decode(response.json["image"]) == output


def test_payload_limit(client):
    response = client.post("/predict", data="x" * (2 * 1024 * 1024), content_type="application/json")
    assert response.status_code == 413
