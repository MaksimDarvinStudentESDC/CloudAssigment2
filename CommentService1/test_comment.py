from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_create_comment():
    response = client.post("/comments", json={
        "portfolio_id": 1,
        "user_id": 1,
        "content": "Nice work"
    })

    assert response.status_code == 200
    assert "status" in response.json()


def test_create_comment_validation():
    response = client.post("/comments", json={
        "content": "No ids"
    })

    assert response.status_code == 422


def test_get_comments_returns_list():
    response = client.get("/comments")

    assert response.status_code == 200
    assert isinstance(response.json(), list)