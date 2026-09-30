def test_create_ticket(client) -> None:
    response = client.post(
        "/api/v1/tickets",
        json={
            "customer_name": "Sarah Miller",
            "customer_email": "SARAH@example.com",
            "subject": "Cannot access my account",
            "message": "I reset my password but I still cannot sign in.",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["id"] == 1
    assert data["customer_email"] == "sarah@example.com"
    assert data["category"] == "account"
    assert data["urgency"] == "normal"
    assert data["language"] == "en"
    assert data["classification_source"] == "fallback"
    assert data["priority"] == "normal"
    assert data["status"] == "new"


def test_get_ticket(client) -> None:
    created = client.post(
        "/api/v1/tickets",
        json={
            "customer_name": "Alex Smith",
            "customer_email": "alex@example.com",
            "subject": "Billing question",
            "message": "I have a question about my latest invoice.",
        },
    ).json()

    response = client.get(f"/api/v1/tickets/{created['id']}")

    assert response.status_code == 200
    assert response.json()["subject"] == "Billing question"


def test_ticket_validation(client) -> None:
    response = client.post(
        "/api/v1/tickets",
        json={
            "customer_name": "",
            "customer_email": "not-an-email",
            "subject": "",
            "message": "x",
        },
    )

    assert response.status_code == 422


def test_missing_ticket_returns_404(client) -> None:
    response = client.get("/api/v1/tickets/999")

    assert response.status_code == 404
