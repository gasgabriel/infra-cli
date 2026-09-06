from dataclasses import dataclass
from datetime import datetime

from .health_rules import (
    CPU_WARNING,
    DISK_WARNING,
    MEMORY_WARNING,
    HealthStatus,
)
from .healthcheck import HealthcheckResult


@dataclass
class Alert:
    """Representa um alerta de infraestrutura."""

    host: str
    metric: str
    value: float | None
    limit: float | None
    severity: str
    message: str
    timestamp: datetime


def generate_alerts(
    results: list[HealthcheckResult],
) -> list[Alert]:
    """Gera alertas a partir dos resultados do healthcheck."""

    alerts = []

    for result in results:
        if result.status == HealthStatus.CONNECTION_ERROR:
            alerts.append(
                Alert(
                    host=result.host,
                    metric="SSH",
                    value=None,
                    limit=None,
                    severity="CRITICAL",
                    message=result.error or "Falha de conexão SSH.",
                    timestamp=datetime.now(),
                )
            )

            continue

        if result.metrics is None:
            continue

        if result.cpu_status in {
            HealthStatus.WARNING,
            HealthStatus.CRITICAL,
        }:
            alerts.append(
                Alert(
                    host=result.host,
                    metric="CPU",
                    value=result.metrics.cpu,
                    limit=CPU_WARNING,
                    severity=result.cpu_status.value,
                    message=(
                        f"Uso de CPU acima do limite: "
                        f"{result.metrics.cpu:.2f}%"
                    ),
                    timestamp=datetime.now(),
                )
            )

        if result.memory_status in {
            HealthStatus.WARNING,
            HealthStatus.CRITICAL,
        }:
            alerts.append(
                Alert(
                    host=result.host,
                    metric="MEMORY",
                    value=result.metrics.memory,
                    limit=MEMORY_WARNING,
                    severity=result.memory_status.value,
                    message=(
                        f"Uso de memória acima do limite: "
                        f"{result.metrics.memory:.2f}%"
                    ),
                    timestamp=datetime.now(),
                )
            )

        if result.disk_status in {
            HealthStatus.WARNING,
            HealthStatus.CRITICAL,
        }:
            alerts.append(
                Alert(
                    host=result.host,
                    metric="DISK",
                    value=result.metrics.disk,
                    limit=DISK_WARNING,
                    severity=result.disk_status.value,
                    message=(
                        f"Uso de disco acima do limite: "
                        f"{result.metrics.disk:.2f}%"
                    ),
                    timestamp=datetime.now(),
                )
            )

    return alerts
