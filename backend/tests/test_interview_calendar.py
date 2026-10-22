from fastapi.testclient import TestClient

VALID = {
    "stage": "technical",
    "starts_at": "2026-11-03T10:00",
    "duration_minutes": 60,
    "interviewer": "Anna Kowalska",
    "location": "Room 2",
    "candidate_ref": "C-14",
}


def make_position(client: TestClient, title: str = "Head of Sales") -> str:
    return client.post("/api/positions", json={"title": title}).json()["slug"]


def plan(client: TestClient, slug: str, **changes: object) -> dict:
    response = client.post(
        f"/api/positions/{slug}/interviews", json={**VALID, **changes}
    )
    assert response.status_code == 201, response.text
    return response.json()


def test_a_planned_interview_is_stored_and_read_back(client: TestClient) -> None:
    slug = make_position(client)

    created = plan(client, slug)

    assert created["status"] == "planned"
    assert created["starts_at"] == "2026-11-03T10:00"
    listed = client.get(f"/api/positions/{slug}/interviews").json()
    assert listed == [created]


def test_interviews_are_listed_in_time_order(client: TestClient) -> None:
    slug = make_position(client)
    late = plan(client, slug, starts_at="2026-11-03T14:00")
    early = plan(client, slug, starts_at="2026-11-03T09:00")
    next_day = plan(client, slug, starts_at="2026-11-04T10:00")

    listed = client.get(f"/api/positions/{slug}/interviews").json()

    assert [i["id"] for i in listed] == [early["id"], late["id"], next_day["id"]]


def test_an_edit_is_stored(client: TestClient) -> None:
    slug = make_position(client)
    created = plan(client, slug)

    response = client.put(
        f"/api/interviews/{created['id']}",
        json={**VALID, "starts_at": "2026-11-03T11:00"},
    )

    assert response.status_code == 200
    assert response.json()["starts_at"] == "2026-11-03T11:00"
    assert client.get(f"/api/positions/{slug}/interviews").json()[0]["starts_at"] == (
        "2026-11-03T11:00"
    )


def test_a_cancelled_interview_stays_listed_and_cannot_be_edited(
    client: TestClient,
) -> None:
    slug = make_position(client)
    created = plan(client, slug)

    cancelled = client.post(f"/api/interviews/{created['id']}/cancel")
    edit = client.put(f"/api/interviews/{created['id']}", json=VALID)

    assert cancelled.status_code == 200
    assert cancelled.json()["status"] == "cancelled"
    assert edit.status_code == 409
    listed = client.get(f"/api/positions/{slug}/interviews").json()
    assert [(i["id"], i["status"]) for i in listed] == [(created["id"], "cancelled")]


def test_cancelling_twice_is_a_conflict(client: TestClient) -> None:
    slug = make_position(client)
    created = plan(client, slug)
    client.post(f"/api/interviews/{created['id']}/cancel")

    response = client.post(f"/api/interviews/{created['id']}/cancel")

    assert response.status_code == 409


def test_duration_must_be_between_5_and_480_minutes(client: TestClient) -> None:
    slug = make_position(client)

    for minutes in (4, 481):
        response = client.post(
            f"/api/positions/{slug}/interviews",
            json={**VALID, "duration_minutes": minutes},
        )
        assert response.status_code == 422
    assert client.get(f"/api/positions/{slug}/interviews").json() == []


def test_a_start_time_with_a_time_zone_is_refused(client: TestClient) -> None:
    slug = make_position(client)

    response = client.post(
        f"/api/positions/{slug}/interviews",
        json={**VALID, "starts_at": "2026-11-03T10:00+01:00"},
    )

    assert response.status_code == 422
    assert client.get(f"/api/positions/{slug}/interviews").json() == []


def test_an_unknown_stage_is_a_404_and_nothing_is_stored(client: TestClient) -> None:
    slug = make_position(client)

    response = client.post(
        f"/api/positions/{slug}/interviews", json={**VALID, "stage": "bogus"}
    )

    assert response.status_code == 404
    assert client.get(f"/api/positions/{slug}/interviews").json() == []


def test_a_missing_interviewer_or_candidate_reference_is_refused(
    client: TestClient,
) -> None:
    slug = make_position(client)

    for field in ("interviewer", "candidate_ref"):
        response = client.post(
            f"/api/positions/{slug}/interviews", json={**VALID, field: "   "}
        )
        assert response.status_code == 422


def test_interviews_of_one_position_do_not_appear_in_another(
    client: TestClient,
) -> None:
    first = make_position(client, "Head of Sales")
    second = make_position(client, "CEO")
    plan(client, first)

    assert client.get(f"/api/positions/{second}/interviews").json() == []


def test_an_unknown_position_is_a_404(client: TestClient) -> None:
    assert client.get("/api/positions/nobody/interviews").status_code == 404


def test_an_unknown_interview_is_a_404(client: TestClient) -> None:
    assert client.put("/api/interviews/999", json=VALID).status_code == 404
    assert client.post("/api/interviews/999/cancel").status_code == 404
