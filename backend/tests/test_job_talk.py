from conftest import FakeClient, job_talk_reply
from fastapi.testclient import TestClient


def create(client: TestClient, title: str = "CEO") -> str:
    response = client.post("/api/positions", json={"title": title})
    assert response.status_code == 201
    return response.json()["slug"]


def test_creating_a_position_rejects_duplicates_and_empty_slugs(
    client: TestClient,
) -> None:
    create(client)

    assert client.post("/api/positions", json={"title": "ceo"}).status_code == 409
    assert client.post("/api/positions", json={"title": "!!!"}).status_code == 422


def test_chat_returns_reply_and_pending_draft_without_writing_hiring(
    client: TestClient, fake_client: FakeClient, settings
) -> None:
    slug = create(client)
    fake_client.replies = [job_talk_reply("# CEO\n\nDraft one.")]

    response = client.post(
        f"/api/positions/{slug}/chat", json={"message": "Start a draft"}
    )

    body = response.json()
    assert response.status_code == 200
    assert [m["role"] for m in body["messages"]] == ["user", "assistant"]
    assert body["draft"]["text"] == "# CEO\n\nDraft one."
    assert body["draft"]["status"] == "pending"
    assert not (settings.hiring_dir / slug).exists()


def test_prompt_contains_only_hiring_inputs(
    client: TestClient, fake_client: FakeClient, settings
) -> None:
    slug = create(client)
    folder = settings.hiring_dir / slug
    folder.mkdir(parents=True)
    (folder / f"{slug}.md").write_text("# CEO\n\nExisting text.\n", encoding="utf-8")
    fake_client.replies = [job_talk_reply("# CEO\n\nNew.")]

    client.post(f"/api/positions/{slug}/chat", json={"message": "Make it shorter"})

    _, prompt = fake_client.calls[0]
    assert "Existing text." in prompt
    assert "Make it shorter" in prompt
    assert "candidate" not in prompt.lower()


def test_accept_writes_the_edited_text_and_links_the_ai_output(
    client: TestClient, fake_client: FakeClient, settings
) -> None:
    slug = create(client)
    fake_client.replies = [job_talk_reply("# CEO\n\nProposal.")]
    draft = client.post(f"/api/positions/{slug}/chat", json={"message": "go"}).json()[
        "draft"
    ]

    response = client.post(
        f"/api/drafts/{draft['id']}/decision",
        json={"action": "edit", "text": "# CEO\n\nEdited by hand."},
    )

    assert response.status_code == 200
    assert response.json() == {"status": "accepted", "path": f"hiring/{slug}/{slug}.md"}
    written = (settings.hiring_dir / slug / f"{slug}.md").read_text(encoding="utf-8")
    assert "Edited by hand." in written
    assert "Proposal." not in written
    assert "AI output" in written


def test_reject_writes_nothing_and_closes_the_draft(
    client: TestClient, fake_client: FakeClient, settings
) -> None:
    slug = create(client)
    fake_client.replies = [job_talk_reply("# CEO\n\nNo.")]
    draft = client.post(f"/api/positions/{slug}/chat", json={"message": "go"}).json()[
        "draft"
    ]

    response = client.post(
        f"/api/drafts/{draft['id']}/decision", json={"action": "reject"}
    )

    assert response.json() == {"status": "rejected", "path": None}
    assert not (settings.hiring_dir / slug).exists()
    assert client.get(f"/api/positions/{slug}/chat").json()["draft"] is None


def test_a_new_proposal_supersedes_the_pending_one(
    client: TestClient, fake_client: FakeClient
) -> None:
    slug = create(client)
    fake_client.replies = [job_talk_reply("first"), job_talk_reply("second")]
    client.post(f"/api/positions/{slug}/chat", json={"message": "one"})
    client.post(f"/api/positions/{slug}/chat", json={"message": "two"})

    pending = client.get(f"/api/positions/{slug}/chat").json()["draft"]

    assert pending["text"] == "second"


def test_unreadable_reply_is_a_502_and_the_raw_output_is_recorded(
    client: TestClient, fake_client: FakeClient
) -> None:
    slug = create(client)
    fake_client.replies = ["no json here"]

    response = client.post(f"/api/positions/{slug}/chat", json={"message": "go"})

    assert response.status_code == 502
    assert "AI output" in response.json()["detail"]
    assert client.get(f"/api/positions/{slug}/chat").json()["draft"] is None


def test_missing_position_is_a_404(client: TestClient) -> None:
    assert client.get("/api/positions/nope/chat").status_code == 404


def test_the_next_prompt_does_not_carry_the_provenance_line(
    client: TestClient, fake_client: FakeClient
) -> None:
    slug = create(client)
    fake_client.replies = [
        job_talk_reply("# CEO\n\nFirst."),
        job_talk_reply("# CEO\n\nSecond."),
    ]
    draft = client.post(f"/api/positions/{slug}/chat", json={"message": "go"}).json()[
        "draft"
    ]
    client.post(f"/api/drafts/{draft['id']}/decision", json={"action": "approve"})

    client.post(f"/api/positions/{slug}/chat", json={"message": "again"})

    _, prompt = fake_client.calls[1]
    assert "First." in prompt
    assert "AI output" not in prompt
    shown = client.get(f"/api/positions/{slug}/job-description").json()["text"]
    assert shown == "# CEO\n\nFirst.\n"
