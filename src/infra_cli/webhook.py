import os

import requests

from .alerts import Alert


class WebhookError(Exception):
    """Erro durante o envio de um webhook."""


def get_webhook_url() -> str | None:
    """Retorna a URL do webhook configurada no ambiente."""

    return os.getenv("INFRA_WEBHOOK_URL")


def send_alerts(alerts: list[Alert]) -> bool:
    """Envia os alertas para o webhook configurado."""

    if not alerts:
        return True

    url = get_webhook_url()

    if not url:
        return False

    lines = [
        "🚨 ALERTAS DE INFRAESTRUTURA",
        "",
    ]

    for alert in alerts:
        lines.append(
            f"[{alert.severity}] "
            f"{alert.host} - "
            f"{alert.metric}: "
            f"{alert.message}"
        )

    payload = {
        "content": "\n".join(lines)
    }

    try:
        response = requests.post(
            url,
            json=payload,
            timeout=10,
        )

        response.raise_for_status()

    except requests.RequestException as exc:
        raise WebhookError(
            f"Falha ao enviar alertas: {exc}"
        ) from exc

    return True
