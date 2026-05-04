from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_create_portfolio_returns_success():
    response = client.post("/portfolios", json={
        "title": "Art",
        "description": "Test",
        "author_id": 1
    })

    assert response.status_code == 200
    assert "status" in response.json()


def test_create_portfolio_missing_field():
    response = client.post("/portfolios", json={
        "title": "Art"
    })

    # FastAPI validation
    assert response.status_code == 422


def test_get_portfolios_returns_list():
    response = client.get("/portfolios")

    assert response.status_code == 200
    assert isinstance(response.json(), list)