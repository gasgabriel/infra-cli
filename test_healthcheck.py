from infra_cli.healthcheck import check_host
from infra_cli.health_rules import HealthStatus


def fake_execute_command(command):
    """Simula os comandos executados no servidor."""

    if "/proc/stat" in command:
        return {
            "exit_code": 0,
            "stdout": (
                "cpu 100 0 100 700 0 0 0 0 0 0 0\n"
                "cpu 150 0 150 750 0 0 0 0 0 0 0\n"
            ),
            "stderr": "",
        }

    if command == "free -b":
        return {
            "exit_code": 0,
            "stdout": (
                "               total        used        free\n"
                "Mem:      1000000000   500000000   500000000\n"
            ),
            "stderr": "",
        }

    if command == "df -P /":
        return {
            "exit_code": 0,
            "stdout": (
                "Filesystem  1024-blocks  Used  Available Capacity Mounted on\n"
                "/dev/sda1   10000000      5000000 5000000  50% /\n"
            ),
            "stderr": "",
        }

    raise ValueError(f"Comando inesperado: {command}")


def test_healthcheck():
    """Testa o healthcheck com dados simulados."""

    result = check_host(
        host="server-test",
        execute_command=fake_execute_command,
    )

    assert result.error is None

    assert result.metrics is not None

    assert result.metrics.cpu == 66.67
    assert result.metrics.memory == 50.0
    assert result.metrics.disk == 50.0

    assert result.cpu_status is not None
    assert result.memory_status is not None
    assert result.disk_status is not None

    assert result.status is not None

    print("Teste de healthcheck: OK")
    print(f"Host: {result.host}")
    print(f"CPU: {result.metrics.cpu}%")
    print(f"Memória: {result.metrics.memory}%")
    print(f"Disco: {result.metrics.disk}%")
    print(f"Status CPU: {result.cpu_status}")
    print(f"Status memória: {result.memory_status}")
    print(f"Status disco: {result.disk_status}")
    print(f"Status geral: {result.status}")


def fake_execute_command_with_error(command):
    """Simula uma falha na coleta de memória."""

    if "/proc/stat" in command:
        return {
            "exit_code": 0,
            "stdout": (
                "cpu 100 0 100 700 0 0 0 0 0 0 0\n"
                "cpu 150 0 150 750 0 0 0 0 0 0 0\n"
            ),
            "stderr": "",
        }

    if command == "free -b":
        return {
            "exit_code": 1,
            "stdout": "",
            "stderr": "Falha ao executar free.",
        }

    if command == "df -P /":
        return {
            "exit_code": 0,
            "stdout": (
                "Filesystem  1024-blocks  Used  Available Capacity Mounted on\n"
                "/dev/sda1   10000000      5000000 5000000  50% /\n"
            ),
            "stderr": "",
        }

    raise ValueError(f"Comando inesperado: {command}")


def test_healthcheck_error():
    """Testa o comportamento quando ocorre uma falha."""

    result = check_host(
        host="server-error",
        execute_command=fake_execute_command_with_error,
    )

    assert result.metrics is None
    assert result.status == HealthStatus.CONNECTION_ERROR
    assert result.error == "Falha ao executar free."

    print("Teste de tratamento de erro: OK")
    print(f"Host: {result.host}")
    print(f"Erro: {result.error}")


if __name__ == "__main__":
    test_healthcheck()
    test_healthcheck_error()

    print()
    print("Todos os testes passaram!")
