from app.core.config import settings


def test_demo_page_uses_root_path(client, monkeypatch) -> None:
    monkeypatch.setattr(settings, "root_path", "/supportops")

    response = client.get(
        "/demo",
        headers={"x-forwarded-prefix": "/supportops"},
    )

    assert response.status_code == 200


def test_demo_html_contains_runtime_base_placeholder_replacement(client) -> None:
    response = client.get("/demo")

    assert response.status_code == 200
    assert "__APP_BASE__" not in response.text
    assert 'window.APP_BASE = ""' in response.text
