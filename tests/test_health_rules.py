from infra_cli.health_rules import (
    CPU_CRITICAL,
    CPU_WARNING,
    DISK_CRITICAL,
    DISK_WARNING,
    MEMORY_CRITICAL,
    MEMORY_WARNING,
    HealthStatus,
    evaluate_cpu,
    evaluate_disk,
    evaluate_memory,
    evaluate_threshold,
    overall_status,
)


def test_threshold_below_warning():
    assert (
        evaluate_threshold(
            50.0,
            warning=80.0,
            critical=90.0,
        )
        == HealthStatus.OK
    )


def test_threshold_at_warning():
    assert (
        evaluate_threshold(
            80.0,
            warning=80.0,
            critical=90.0,
        )
        == HealthStatus.WARNING
    )


def test_threshold_at_critical():
    assert (
        evaluate_threshold(
            90.0,
            warning=80.0,
            critical=90.0,
        )
        == HealthStatus.CRITICAL
    )


def test_cpu_warning():
    assert evaluate_cpu(CPU_WARNING) == HealthStatus.WARNING


def test_cpu_critical():
    assert evaluate_cpu(CPU_CRITICAL) == HealthStatus.CRITICAL


def test_memory_warning():
    assert evaluate_memory(MEMORY_WARNING) == HealthStatus.WARNING


def test_memory_critical():
    assert evaluate_memory(MEMORY_CRITICAL) == HealthStatus.CRITICAL


def test_disk_warning():
    assert evaluate_disk(DISK_WARNING) == HealthStatus.WARNING


def test_disk_critical():
    assert evaluate_disk(DISK_CRITICAL) == HealthStatus.CRITICAL


def test_overall_status_ok():
    assert (
        overall_status(
            [
                HealthStatus.OK,
                HealthStatus.OK,
                HealthStatus.OK,
            ]
        )
        == HealthStatus.OK
    )


def test_overall_status_warning():
    assert (
        overall_status(
            [
                HealthStatus.OK,
                HealthStatus.WARNING,
                HealthStatus.OK,
            ]
        )
        == HealthStatus.WARNING
    )


def test_overall_status_critical():
    assert (
        overall_status(
            [
                HealthStatus.OK,
                HealthStatus.WARNING,
                HealthStatus.CRITICAL,
            ]
        )
        == HealthStatus.CRITICAL
    )


def test_critical_has_priority_over_warning():
    assert (
        overall_status(
            [
                HealthStatus.CRITICAL,
                HealthStatus.WARNING,
                HealthStatus.OK,
            ]
        )
        == HealthStatus.CRITICAL
    )
