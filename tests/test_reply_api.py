def seed_account_knowledge(client) -> None:
    response = client.post(
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
    assert response.status_code == 201


def test_create_reply_draft_persists_grounded_fallback(client) -> None:
    seed_account_knowledge(client)

    ticket = client.post(
        "/api/v1/tickets",
        json={
            "customer_name": "Sarah Miller",
            "customer_email": "sarah@example.com",
            "subject": "Cannot access my account",
            "message": "I reset my password but I still cannot sign in.",
        },
    ).json()

    response = client.post(f"/api/v1/tickets/{ticket['id']}/draft")

    assert response.status_code == 200
    data = response.json()
    assert data["ticket_id"] == ticket["id"]
    assert data["reply"]
    assert data["source_refs"]
    assert data["source"] == "fallback"

    stored = client.get(f"/api/v1/tickets/{ticket['id']}").json()
    assert stored["draft_reply"] == data["reply"]
    assert stored["status"] == "waiting_review"


def test_reply_draft_without_knowledge_is_safe(client) -> None:
    ticket = client.post(
        "/api/v1/tickets",
        json={
            "customer_name": "Alex Smith",
            "customer_email": "alex@example.com",
            "subject": "Unusual request",
            "message": "I have a question not covered by the help center.",
        },
    ).json()

    response = client.post(f"/api/v1/tickets/{ticket['id']}/draft")

    assert response.status_code == 200
    data = response.json()
    assert data["source_refs"] == []
    assert data["needs_human_review"] is True
    assert data["confidence"] == 0.2
