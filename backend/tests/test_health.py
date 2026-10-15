from fastapi.testclient import TestClient


def test_health_reports_ok_and_subscription_by_default(client: TestClient) -> None:
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "auth_method": "subscription"}


def test_health_reports_api_key_when_the_variable_is_set(
    client: TestClient, monkeypatch
) -> None:
    monkeypatch.setenv("ANTHROPIC_API_KEY", "not-a-real-key")

    assert client.get("/api/health").json()["auth_method"] == "api_key"
