def test_demo_page_loads(client) -> None:
    response = client.get("/demo")

    assert response.status_code == 200
    assert "AIA SupportOps Automation" in response.text
    assert "Human-in-the-loop support operations" in response.text


def test_demo_assets_load(client) -> None:
    css = client.get("/static/demo/style.css")
    js = client.get("/static/demo/app.js")

    assert css.status_code == 200
    assert js.status_code == 200
    assert "metric-grid" in css.text
    assert "refreshAudit" in js.text
