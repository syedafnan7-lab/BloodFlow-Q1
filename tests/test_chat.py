"""Regression checks for the synthetic-scenario chat assistant endpoint."""

from fastapi.testclient import TestClient

from backend.main import create_app


def test_chat_returns_scenario_grounded_critical_demand_summary() -> None:
    client = TestClient(create_app())

    response = client.post(
        "/chat",
        json={"message": "What are our critical unmet demands?", "history": [], "context": {}},
    )

    assert response.status_code == 200
    payload = response.json()
    assert "38" in payload["reply"]
    assert "11" in payload["reply"]
    assert payload["data_citations"]
    assert any(action["type"] == "optimize" for action in payload["suggested_actions"])
