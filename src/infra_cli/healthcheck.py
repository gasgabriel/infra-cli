from collections.abc import Callable
from dataclasses import dataclass

from .health_rules import (
    HealthStatus,
    evaluate_cpu,
    evaluate_disk,
    evaluate_memory,
    overall_status,
)

from .metrics import (
    ServerMetrics,
    get_cpu_usage,
    get_disk_usage,
    get_memory_usage,
)


@dataclass
class HealthcheckResult:
    """Resultado do healthcheck de um servidor."""

    host: str
    metrics: ServerMetrics | None = None

    cpu_status: HealthStatus | None = None
    memory_status: HealthStatus | None = None
    disk_status: HealthStatus | None = None

    status: HealthStatus | None = None

    error: str | None = None


def check_host(host: str, execute_command) -> HealthcheckResult:
    """Executa o healthcheck de um servidor."""

    try:
        cpu = get_cpu_usage(execute_command)
        memory = get_memory_usage(execute_command)
        disk = get_disk_usage(execute_command)

        metrics = ServerMetrics(
            cpu=cpu,
            memory=memory,
            disk=disk,
        )

        cpu_status = evaluate_cpu(cpu)
        memory_status = evaluate_memory(memory)
        disk_status = evaluate_disk(disk)

        status = overall_status(
            [
                cpu_status,
                memory_status,
                disk_status,
            ]
        )

        return HealthcheckResult(
            host=host,
            metrics=metrics,
            cpu_status=cpu_status,
            memory_status=memory_status,
            disk_status=disk_status,
            status=status,
        )

    except Exception as exc:
        return HealthcheckResult(
            host=host,
            status=HealthStatus.CONNECTION_ERROR,
            error=str(exc),
        )


def run_healthchecks(
    servers: list[dict],
    passphrase: str,
    ssh_client_factory: Callable,
) -> list[HealthcheckResult]:
    """Executa healthchecks em uma lista de servidores."""

    results = []

    for server in servers:
        client = ssh_client_factory(
            hostname=server["hostname"],
            username=server["username"],
            port=server["port"],
        )

        try:
            client.connect(passphrase=passphrase)

            result = check_host(
                server["name"],
                client.execute,
            )

            results.append(result)

        except ConnectionError as exc:
            results.append(
                HealthcheckResult(
                    host=server["name"],
                    status=HealthStatus.CONNECTION_ERROR,
                    error=str(exc),
                )
            )

        finally:
            client.close()

    return results
