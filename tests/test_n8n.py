from app.core.config import settings
from app.integrations.n8n import send_support_webhook


def test_unconfigured_webhook_is_skipped(monkeypatch) -> None:
    monkeypatch.setattr(settings, "n8n_webhook_url", None)

    result = send_support_webhook({"event": "test"})

    assert result.status == "skipped"
    assert result.attempts == 0
    assert result.last_error is None
