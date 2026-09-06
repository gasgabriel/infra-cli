from enum import Enum


class HealthStatus(str, Enum):
    OK = "OK"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"
    CONNECTION_ERROR = "CONNECTION_ERROR"


CPU_WARNING = 80.0
CPU_CRITICAL = 90.0

MEMORY_WARNING = 80.0
MEMORY_CRITICAL = 90.0

DISK_WARNING = 80.0
DISK_CRITICAL = 90.0


def evaluate_threshold(
    value: float,
    warning: float,
    critical: float,
) -> HealthStatus:
    """Classifica um valor de acordo com limites de saúde."""

    if value >= critical:
        return HealthStatus.CRITICAL

    if value >= warning:
        return HealthStatus.WARNING

    return HealthStatus.OK


def evaluate_cpu(value: float) -> HealthStatus:
    """Avalia o uso da CPU."""

    return evaluate_threshold(
        value,
        warning=CPU_WARNING,
        critical=CPU_CRITICAL,
    )


def evaluate_memory(value: float) -> HealthStatus:
    """Avalia o uso da memória."""

    return evaluate_threshold(
        value,
        warning=MEMORY_WARNING,
        critical=MEMORY_CRITICAL,
    )


def evaluate_disk(value: float) -> HealthStatus:
    """Avalia o uso do disco."""

    return evaluate_threshold(
        value,
        warning=DISK_WARNING,
        critical=DISK_CRITICAL,
    )


def overall_status(statuses: list[HealthStatus]) -> HealthStatus:
    """Determina o estado geral a partir dos estados das métricas."""

    if HealthStatus.CRITICAL in statuses:
        return HealthStatus.CRITICAL

    if HealthStatus.WARNING in statuses:
        return HealthStatus.WARNING

    return HealthStatus.OK
