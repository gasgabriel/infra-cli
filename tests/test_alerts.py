from datetime import datetime

from infra_cli.alerts import generate_alerts
from infra_cli.health_rules import HealthStatus
from infra_cli.healthcheck import HealthcheckResult
from infra_cli.metrics import ServerMetrics


def create_result(
    host="server01",
    cpu=20.0,
    memory=30.0,
    disk=40.0,
    cpu_status=HealthStatus.OK,
    memory_status=HealthStatus.OK,
    disk_status=HealthStatus.OK,
    status=HealthStatus.OK,
    error=None,
):
    return HealthcheckResult(
        host=host,
        metrics=ServerMetrics(
            cpu=cpu,
            memory=memory,
            disk=disk,
        ) if error is None else None,
        cpu_status=cpu_status if error is None else None,
        memory_status=memory_status if error is None else None,
        disk_status=disk_status if error is None else None,
        status=status,
        error=error,
    )


def test_no_alerts_when_server_is_ok():
    result = create_result()

    alerts = generate_alerts([result])

    assert alerts == []


def test_generates_cpu_warning():
    result = create_result(
        cpu=85.0,
        cpu_status=HealthStatus.WARNING,
        status=HealthStatus.WARNING,
    )

    alerts = generate_alerts([result])

    assert len(alerts) == 1

    alert = alerts[0]

    assert alert.host == "server01"
    assert alert.metric == "CPU"
    assert alert.value == 85.0
    assert alert.severity == "WARNING"


def test_generates_cpu_critical():
    result = create_result(
        cpu=95.0,
        cpu_status=HealthStatus.CRITICAL,
        status=HealthStatus.CRITICAL,
    )

    alerts = generate_alerts([result])

    assert len(alerts) == 1

    alert = alerts[0]

    assert alert.host == "server01"
    assert alert.metric == "CPU"
    assert alert.value == 95.0
    assert alert.severity == "CRITICAL"


def test_generates_memory_alert():
    result = create_result(
        memory=91.0,
        memory_status=HealthStatus.CRITICAL,
        status=HealthStatus.CRITICAL,
    )

    alerts = generate_alerts([result])

    assert len(alerts) == 1

    alert = alerts[0]

    assert alert.metric == "MEMORY"
    assert alert.value == 91.0
    assert alert.severity == "CRITICAL"


def test_generates_disk_alert():
    result = create_result(
        disk=82.0,
        disk_status=HealthStatus.WARNING,
        status=HealthStatus.WARNING,
    )

    alerts = generate_alerts([result])

    assert len(alerts) == 1

    alert = alerts[0]

    assert alert.metric == "DISK"
    assert alert.value == 82.0
    assert alert.severity == "WARNING"


def test_generates_connection_alert():
    result = create_result(
        host="server03",
        status=HealthStatus.CONNECTION_ERROR,
        error="Timeout ao conectar ao host server03",
    )

    alerts = generate_alerts([result])

    assert len(alerts) == 1

    alert = alerts[0]

    assert alert.host == "server03"
    assert alert.metric == "SSH"
    assert alert.value is None
    assert alert.limit is None
    assert alert.severity == "CRITICAL"
    assert alert.message == "Timeout ao conectar ao host server03"


def test_generates_multiple_alerts():
    result = create_result(
        cpu=95.0,
        memory=92.0,
        disk=85.0,
        cpu_status=HealthStatus.CRITICAL,
        memory_status=HealthStatus.CRITICAL,
        disk_status=HealthStatus.WARNING,
        status=HealthStatus.CRITICAL,
    )

    alerts = generate_alerts([result])

    assert len(alerts) == 3

    metrics = {
        alert.metric
        for alert in alerts
    }

    assert metrics == {
        "CPU",
        "MEMORY",
        "DISK",
    }


def test_alert_has_timestamp():
    result = create_result(
        cpu=95.0,
        cpu_status=HealthStatus.CRITICAL,
        status=HealthStatus.CRITICAL,
    )

    alerts = generate_alerts([result])

    assert isinstance(
        alerts[0].timestamp,
        datetime,
    )

def test_skips_result_without_metrics():
    from types import SimpleNamespace


    result = SimpleNamespace(
        host="server01",
        status=HealthStatus.OK,
        metrics=None,
        cpu_status=HealthStatus.OK,
        memory_status=HealthStatus.OK,
        disk_status=HealthStatus.OK,
        error=None,
    )

    alerts = generate_alerts([result])

    assert alerts == []

