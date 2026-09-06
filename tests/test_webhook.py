from datetime import datetime

import pytest
import requests

from infra_cli.alerts import Alert
from infra_cli.webhook import (
    WebhookError,
    get_webhook_url,
    send_alerts,
)

def create_alert():
    return Alert(
        host="server01",
        metric="CPU",
        value=95.0,
        limit=90.0,
        severity="CRITICAL",
        message="Uso de CPU acima do limite: 95.00%",
        timestamp=datetime.now(),
    )


def test_get_webhook_url(monkeypatch):
    monkeypatch.setenv(
        "INFRA_WEBHOOK_URL",
        "https://example.com/webhook",
    )

    assert (
        get_webhook_url()
        == "https://example.com/webhook"
    )


def test_get_webhook_url_when_not_configured(monkeypatch):
    monkeypatch.delenv(
        "INFRA_WEBHOOK_URL",
        raising=False,
    )

    assert get_webhook_url() is None


def test_send_alerts_without_alerts(monkeypatch):
    result = send_alerts([])

    assert result is True


def test_send_alerts_without_webhook(monkeypatch):
    monkeypatch.delenv(
        "INFRA_WEBHOOK_URL",
        raising=False,
    )

    alerts = [create_alert()]

    result = send_alerts(alerts)

    assert result is False


def test_send_alerts_success(monkeypatch):
    monkeypatch.setenv(
        "INFRA_WEBHOOK_URL",
        "https://example.com/webhook",
    )

    class FakeResponse:
        def raise_for_status(self):
            pass

    def fake_post(url, json, timeout):
        assert url == "https://example.com/webhook"
        assert timeout == 10

        assert "content" in json
        assert "server01" in json["content"]
        assert "CPU" in json["content"]
        assert "CRITICAL" in json["content"]

        return FakeResponse()

    monkeypatch.setattr(
        "infra_cli.webhook.requests.post",
        fake_post,
    )

    alerts = [create_alert()]

    result = send_alerts(alerts)

    assert result is True


def test_send_alerts_http_error(monkeypatch):
    monkeypatch.setenv(
        "INFRA_WEBHOOK_URL",
        "https://example.com/webhook",
    )

    class FakeResponse:
        def raise_for_status(self):
            raise requests.HTTPError("500 Server Error")

    def fake_post(url, json, timeout):
        return FakeResponse()

    import requests

    monkeypatch.setattr(
        "infra_cli.webhook.requests.post",
        fake_post,
    )

    alerts = [create_alert()]

    with pytest.raises(WebhookError):
        send_alerts(alerts)


def test_send_alerts_connection_error(monkeypatch):
    monkeypatch.setenv(
        "INFRA_WEBHOOK_URL",
        "https://example.com/webhook",
    )

    import requests

    def fake_post(url, json, timeout):
        raise requests.ConnectionError(
            "Connection refused"
        )

    monkeypatch.setattr(
        "infra_cli.webhook.requests.post",
        fake_post,
    )

    alerts = [create_alert()]

    with pytest.raises(WebhookError):
        send_alerts(alerts)
