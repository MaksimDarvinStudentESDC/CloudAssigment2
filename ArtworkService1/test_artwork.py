from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_get_artworks():
    response = client.get("/artworks")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_create_artwork():
    response = client.post("/artworks", json={
        "title": "Test Art",
        "description": "Nice",
        "portfolio_id": 1
    })

    assert response.status_code == 200
    assert "status" in response.json()


def test_create_artwork_validation():
    response = client.post("/artworks", json={
        "title": "Missing fields"
    })

    assert response.status_code == 422