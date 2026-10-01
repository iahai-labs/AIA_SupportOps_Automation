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

    client.post(f"/api/v1/tickets/{ticket['id']}/draft")
    return ticket["id"]


def test_audit_trail_records_ticket_lifecycle(client) -> None:
    ticket_id = create_ticket_with_draft(client)

    client.post(
        f"/api/v1/tickets/{ticket_id}/approve",
        json={"reviewed_by": "Support Agent"},
    )

    response = client.get(f"/api/v1/tickets/{ticket_id}/audit")

    assert response.status_code == 200
    events = [item["event_type"] for item in response.json()]
    assert "ticket.created" in events
    assert "reply.drafted" in events
    assert "review.approved" in events
    assert any(event.startswith("automation.") for event in events)


def test_missing_ticket_audit_returns_404(client) -> None:
    response = client.get("/api/v1/tickets/999999/audit")
    assert response.status_code == 404
