def create_approved_ticket(client) -> int:
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
    approved = client.post(
        f"/api/v1/tickets/{ticket['id']}/approve",
        json={"reviewed_by": "Support Agent"},
    )
    assert approved.status_code == 200
    return ticket["id"]


def test_skipped_automation_can_retry(client) -> None:
    ticket_id = create_approved_ticket(client)

    response = client.post(f"/api/v1/tickets/{ticket_id}/automation/retry")

    assert response.status_code == 200
    data = response.json()
    assert data["automation_status"] == "skipped"
    assert data["automation_attempts"] == 0
