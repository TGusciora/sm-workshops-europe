from app.stages import STAGES
from conftest import FakeClient, questions_reply
from fastapi import FastAPI
from fastapi.testclient import TestClient


def setup_position_with_jd(
    client: TestClient, settings, text: str = "# CEO\n\nLead the company.\n"
) -> str:
    slug = client.post("/api/positions", json={"title": "CEO"}).json()["slug"]
    folder = settings.hiring_dir / slug
    folder.mkdir(parents=True, exist_ok=True)
    (folder / f"{slug}.md").write_text(text, encoding="utf-8")
    return slug


def propose(client: TestClient, slug: str, stage: str = "screening") -> dict:
    response = client.post(f"/api/positions/{slug}/stages/{stage}/questions")
    assert response.status_code == 200, response.text
    return response.json()


def test_stages_are_listed(client: TestClient) -> None:
    assert client.get("/api/stages").json() == {"stages": list(STAGES)}


def test_proposing_needs_a_job_description_first(client: TestClient) -> None:
    slug = client.post("/api/positions", json={"title": "CEO"}).json()["slug"]

    response = client.post(f"/api/positions/{slug}/stages/screening/questions")

    assert response.status_code == 409


def test_unknown_stage_is_a_404(client: TestClient, settings) -> None:
    slug = setup_position_with_jd(client, settings)

    assert (
        client.post(f"/api/positions/{slug}/stages/bogus/questions").status_code == 404
    )


def test_proposals_are_stored_but_not_final(
    client: TestClient, fake_client: FakeClient, settings
) -> None:
    slug = setup_position_with_jd(client, settings)
    fake_client.replies = [questions_reply(2)]

    body = propose(client, slug)

    assert body["confirmed"] is False
    assert [q["status"] for q in body["questions"]] == ["proposed", "proposed"]
    assert body["questions"][0]["purpose"] == "Purpose 1"
    assert body["questions"][0]["good_answer"] == "Good answer 1"


def test_each_question_is_decided_on_its_own(
    client: TestClient, fake_client: FakeClient, settings
) -> None:
    slug = setup_position_with_jd(client, settings)
    fake_client.replies = [questions_reply(3)]
    first, second, third = (q["id"] for q in propose(client, slug)["questions"])

    client.post(f"/api/questions/{first}/decision", json={"action": "approve"})
    edited = client.post(
        f"/api/questions/{second}/decision",
        json={"action": "edit", "question": "Reworded?"},
    ).json()
    client.post(f"/api/questions/{third}/decision", json={"action": "reject"})

    assert edited["question"] == "Reworded?"
    assert edited["status"] == "approved"
    statuses = [
        q["status"]
        for q in client.get(f"/api/positions/{slug}/stages/screening/questions").json()[
            "questions"
        ]
    ]
    assert statuses == ["approved", "approved", "rejected"]


def test_confirming_stores_the_approved_set_and_locks_it(
    client: TestClient, fake_client: FakeClient, settings
) -> None:
    slug = setup_position_with_jd(client, settings)
    fake_client.replies = [questions_reply(2)]
    first, second = (q["id"] for q in propose(client, slug)["questions"])
    client.post(f"/api/questions/{first}/decision", json={"action": "approve"})
    client.post(f"/api/questions/{second}/decision", json={"action": "reject"})

    confirmed = client.post(f"/api/positions/{slug}/stages/screening/confirm").json()

    assert confirmed["confirmed"] is True
    read_back = client.get(f"/api/positions/{slug}/stages/screening/questions").json()
    assert read_back["confirmed"] is True
    assert [q["status"] for q in read_back["questions"]] == ["approved", "rejected"]
    assert (
        client.post(
            f"/api/questions/{second}/decision", json={"action": "approve"}
        ).status_code
        == 409
    )


def test_confirming_needs_at_least_one_approved_question(
    client: TestClient, fake_client: FakeClient, settings
) -> None:
    slug = setup_position_with_jd(client, settings)
    fake_client.replies = [questions_reply(1)]
    propose(client, slug)

    assert (
        client.post(f"/api/positions/{slug}/stages/screening/confirm").status_code
        == 409
    )


def test_prompt_uses_the_job_description_and_approved_questions_of_that_stage_only(
    client: TestClient, fake_client: FakeClient, settings
) -> None:
    slug = setup_position_with_jd(client, settings)
    fake_client.replies = [questions_reply(1), questions_reply(1)]
    (question_id,) = (q["id"] for q in propose(client, slug)["questions"])
    client.post(f"/api/questions/{question_id}/decision", json={"action": "approve"})

    propose(client, slug, stage="technical")

    _, prompt = fake_client.calls[1]
    assert "Lead the company." in prompt
    assert "Interview stage: technical" in prompt
    assert "(none yet)" in prompt
    assert "Question 1?" not in prompt


def test_a_proposal_and_its_decisions_are_recorded_as_ai_output(
    app: FastAPI, client: TestClient, fake_client: FakeClient, settings
) -> None:
    slug = setup_position_with_jd(client, settings)
    fake_client.replies = [questions_reply(1)]
    (question,) = propose(client, slug)["questions"]

    client.post(f"/api/questions/{question['id']}/decision", json={"action": "approve"})

    repo = app.state.repo
    rows = repo.conn.execute(
        "SELECT kind, status, model_id, prompt_version FROM ai_outputs"
    ).fetchall()
    assert [tuple(r) for r in rows] == [
        ("interview_questions", "ok", "fake-model", "interview-questions-v1")
    ]
    decisions = repo.conn.execute(
        "SELECT action, subject_type FROM decisions"
    ).fetchall()
    assert [tuple(d) for d in decisions] == [("approve", "question")]


def test_an_unreadable_proposal_is_a_502_and_stores_nothing(
    client: TestClient, fake_client: FakeClient, settings
) -> None:
    slug = setup_position_with_jd(client, settings)
    fake_client.replies = ["[not valid json"]

    response = client.post(f"/api/positions/{slug}/stages/screening/questions")

    assert response.status_code == 502
    assert propose_count(client, slug) == 0


def propose_count(client: TestClient, slug: str) -> int:
    return len(
        client.get(f"/api/positions/{slug}/stages/screening/questions").json()[
            "questions"
        ]
    )
