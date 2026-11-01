import pytest
from backend.app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_health_check(client):
    res = client.get("/api/health")
    assert res.status_code == 200
    assert res.json["status"] == "healthy"


def test_append_event_api(client):
    payload = {"event_type": "SYSTEM_START", "actor": "admin", "data": {"mode": "prod"}}
    res = client.post("/api/events", json=payload)
    assert res.status_code == 201
    assert res.json["block"]["actor"] == "admin"


def test_get_chain_and_verify_api(client):
    chain_res = client.get("/api/chain")
    assert chain_res.status_code == 200
    assert "chain" in chain_res.json
    verify_res = client.get("/api/verify")
    assert verify_res.status_code == 200
    assert verify_res.json["valid"] is True
