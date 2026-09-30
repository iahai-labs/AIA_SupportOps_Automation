def create_ticket_with_draft(client) -> int:
    client.post(
        "/api/v1/knowledge",
        json={
            "title": "Account login troubleshooting",
            "content": (
                "For account login problems, use the password reset link and then "
                "retry sign in using a new browser session."
            ),
            "category": "account",
            "source": "support-handbook",
        },
    )

    ticket = client.post(
        "/api/v1/tickets",
        json={
            "customer_name": "Sarah Miller",
            "customer_email": "sarah@example.com",
            "subject": "Cannot access my account",
            "message": "I reset my password but I still cannot sign in.",
        },
    ).json()

    draft_response = client.post(f"/api/v1/tickets/{ticket['id']}/draft")
    assert draft_response.status_code == 200

    return ticket["id"]


def test_approve_ticket(client) -> None:
    ticket_id = create_ticket_with_draft(client)

    response = client.post(
        f"/api/v1/tickets/{ticket_id}/approve",
        json={
            "reviewed_by": "Support Agent",
            "note": "Verified against the support handbook.",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "approved"
    assert data["approved_reply"]
    assert data["reviewed_by"] == "Support Agent"
    assert data["reviewed_at"] is not None

    stored = client.get(f"/api/v1/tickets/{ticket_id}").json()
    assert stored["status"] == "approved"
    assert stored["approved_reply"] == data["approved_reply"]


def test_approve_allows_human_edit(client) -> None:
    ticket_id = create_ticket_with_draft(client)

    response = client.post(
        f"/api/v1/tickets/{ticket_id}/approve",
        json={
            "reviewed_by": "Senior Agent",
            "approved_reply": "Human-edited final response.",
        },
    )

    assert response.status_code == 200
    assert response.json()["approved_reply"] == "Human-edited final response."


def test_reject_ticket(client) -> None:
    ticket_id = create_ticket_with_draft(client)

    response = client.post(
        f"/api/v1/tickets/{ticket_id}/reject",
        json={
            "reviewed_by": "Support Lead",
            "note": "Needs account investigation.",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "rejected"
    assert data["approved_reply"] == ""


def test_cannot_review_ticket_twice(client) -> None:
    ticket_id = create_ticket_with_draft(client)

    first = client.post(
        f"/api/v1/tickets/{ticket_id}/approve",
        json={"reviewed_by": "Support Agent"},
    )
    assert first.status_code == 200

    second = client.post(
        f"/api/v1/tickets/{ticket_id}/reject",
        json={"reviewed_by": "Support Lead"},
    )

    assert second.status_code == 409
