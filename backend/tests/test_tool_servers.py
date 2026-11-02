from pathlib import Path

import pytest
from app.config import Settings
from app.main import create_app
from fastapi.testclient import TestClient

INTERVIEWER = {"Authorization": "Bearer interviewer-token"}
MANAGER = {"Authorization": "Bearer manager-token"}


@pytest.fixture
def settings(tmp_path: Path) -> Settings:
    ceo = tmp_path / "hiring" / "ceo"
    ceo.mkdir(parents=True)
    (ceo / "ceo.md").write_text(
        "# Position: CEO\n\n## Must-have requirements\n\n- 8+ years of leadership.\n",
        encoding="utf-8",
    )
    return Settings(
        data_dir=tmp_path / "data",
        hiring_dir=tmp_path / "hiring",
        api_tokens={"interviewer-token": "interviewer", "manager-token": "manager"},
    )


def names(items: list[dict[str, object]]) -> list[str]:
    return sorted(str(item["name"]) for item in items)


def test_missing_or_unknown_token_is_rejected(client: TestClient) -> None:
    assert client.get("/api/tool-servers").status_code == 401
    bad = {"Authorization": "Bearer nope"}
    assert client.get("/api/tool-servers", headers=bad).status_code == 401


def test_interviewer_sees_only_servers_it_may_use(client: TestClient) -> None:
    response = client.get("/api/tool-servers", headers=INTERVIEWER)

    assert names(response.json()) == ["scheduling", "screening"]


def test_manager_sees_every_server(client: TestClient) -> None:
    response = client.get("/api/tool-servers", headers=MANAGER)

    assert names(response.json()) == ["crm", "scheduling", "screening"]


def test_server_search_matches_capabilities(client: TestClient) -> None:
    found = client.get("/api/tool-servers?capability=calendar", headers=MANAGER)
    hidden = client.get("/api/tool-servers?capability=crm", headers=INTERVIEWER)

    assert names(found.json()) == ["scheduling"]
    assert hidden.json() == []


def test_tool_search_is_limited_to_one_server_and_role(client: TestClient) -> None:
    screening = client.get(
        "/api/tool-servers/screening/tools?q=criteria", headers=INTERVIEWER
    )
    crm_as_interviewer = client.get("/api/tool-servers/crm/tools", headers=INTERVIEWER)
    crm_as_manager = client.get(
        "/api/tool-servers/crm/tools?q=interview note", headers=MANAGER
    )

    assert [t["name"] for t in screening.json()] == ["get_job_criteria"]
    assert crm_as_interviewer.status_code == 404
    assert [t["name"] for t in crm_as_manager.json()] == ["write_interview_note"]


def test_screening_criteria_come_from_the_job_description(client: TestClient) -> None:
    response = client.post(
        "/api/tool-servers/screening/tools/get_job_criteria/call",
        json={"arguments": {"position": "ceo"}},
        headers=INTERVIEWER,
    )

    assert response.status_code == 200
    assert "8+ years of leadership" in response.json()["result"]["job_description"]


def test_interviewer_cannot_call_a_manager_tool(client: TestClient) -> None:
    response = client.post(
        "/api/tool-servers/crm/tools/write_interview_note/call",
        json={"arguments": {"candidate_id": "c-001", "note": "x", "assessment": "yes"}},
        headers=INTERVIEWER,
    )

    assert response.status_code == 404


def test_scheduling_proposes_but_does_not_book(client: TestClient) -> None:
    response = client.post(
        "/api/tool-servers/scheduling/tools/propose_appointment/call",
        json={"arguments": {"candidate_id": "c-001", "slot": "2026-11-10T10:00"}},
        headers=INTERVIEWER,
    )

    assert response.json()["result"]["status"] == "proposed"


def test_manager_note_is_persisted_across_a_restart(
    settings: Settings, client: TestClient
) -> None:
    written = client.post(
        "/api/tool-servers/crm/tools/write_interview_note/call",
        json={
            "arguments": {
                "candidate_id": "c-001",
                "note": "Strong systems.",
                "assessment": "yes",
            }
        },
        headers=MANAGER,
    )
    restarted = TestClient(create_app(settings))
    record = restarted.post(
        "/api/tool-servers/crm/tools/get_candidate_record/call",
        json={"arguments": {"candidate_id": "c-001"}},
        headers=MANAGER,
    )

    assert written.status_code == 200
    assert record.json()["result"]["notes"] == [
        {"note": "Strong systems.", "assessment": "yes"}
    ]


def test_missing_argument_asks_the_user_before_running(client: TestClient) -> None:
    url = "/api/tool-servers/scheduling/tools/propose_appointment/call"
    asked = client.post(
        url, json={"arguments": {"candidate_id": "c-001"}}, headers=INTERVIEWER
    )
    answered = client.post(
        url,
        json={"arguments": {"candidate_id": "c-001", "slot": "2026-11-10T10:00"}},
        headers=INTERVIEWER,
    )

    body = asked.json()
    assert body["status"] == "input_required"
    assert body["result"] is None
    assert body["elicitation"]["requestedSchema"]["required"] == ["slot"]
    assert list(body["elicitation"]["requestedSchema"]["properties"]) == ["slot"]
    assert answered.json()["status"] == "completed"


def test_empty_string_counts_as_missing(client: TestClient) -> None:
    response = client.post(
        "/api/tool-servers/screening/tools/get_candidate_profile/call",
        json={"arguments": {"candidate_id": ""}},
        headers=INTERVIEWER,
    )

    assert response.json()["elicitation"]["requestedSchema"]["required"] == [
        "candidate_id"
    ]


@pytest.mark.parametrize(
    ("tool", "arguments", "status"),
    [
        ("get_candidate_profile", {"candidate_id": "c-999"}, 404),
        ("get_job_criteria", {"position": "../secrets"}, 422),
        ("get_job_criteria", {"position": "nope"}, 404),
        ("propose_appointment", {"candidate_id": "c-001", "slot": "never"}, 422),
    ],
)
def test_bad_calls_get_a_clear_status(
    client: TestClient, tool: str, arguments: dict[str, str], status: int
) -> None:
    server = "scheduling" if tool == "propose_appointment" else "screening"
    response = client.post(
        f"/api/tool-servers/{server}/tools/{tool}/call",
        json={"arguments": arguments},
        headers=INTERVIEWER,
    )

    assert response.status_code == status
