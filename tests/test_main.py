from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_predict_positive():
    response = client.post(
        "/predict",
        json={"text": "ce produit est excellent et super"}
    )

    assert response.status_code == 200
    assert response.json()["label"] == "POSITIVE"


def test_predict_negative():
    response = client.post(
        "/predict",
        json={"text": "ce produit est horrible et mauvais"}
    )

    assert response.status_code == 200
    assert response.json()["label"] == "NEGATIVE"