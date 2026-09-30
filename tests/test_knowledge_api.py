def test_create_knowledge_article(client) -> None:
    response = client.post(
        "/api/v1/knowledge",
        json={
            "title": "Reset password",
            "content": "Use the password reset page, then retry login in a fresh session.",
            "category": "account",
            "source": "support-handbook",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Reset password"
    assert data["category"] == "account"
    assert data["source"] == "support-handbook"


def test_ticket_knowledge_endpoint(client) -> None:
    client.post(
        "/api/v1/knowledge",
        json={
            "title": "Account login troubleshooting",
            "content": (
                "For account login problems, reset the password and retry sign in "
                "using a new browser session."
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

    response = client.get(f"/api/v1/tickets/{ticket['id']}/knowledge")

    assert response.status_code == 200
    data = response.json()
    assert data["matches"]
    assert data["matches"][0]["source"] == "support-handbook"
    assert data["confidence"] > 0
