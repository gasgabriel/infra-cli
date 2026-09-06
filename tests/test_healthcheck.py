from infra_cli.health_rules import HealthStatus
from infra_cli.healthcheck import check_host


def create_command_responses(
    cpu_output,
    memory_output,
    disk_output,
):
    def fake_execute(command):
        if "/proc/stat" in command:
            return {
                "stdout": cpu_output,
                "stderr": "",
                "exit_code": 0,
            }

        if command == "free -b":
            return {
                "stdout": memory_output,
                "stderr": "",
                "exit_code": 0,
            }

        if command == "df -P /":
            return {
                "stdout": disk_output,
                "stderr": "",
                "exit_code": 0,
            }

        raise AssertionError(
            f"Comando inesperado: {command}"
        )

    return fake_execute


CPU_OUTPUT = """\
cpu  100 20 30 850 0 0 0 0 0 0 0
cpu  120 25 40 915 0 0 0 0 0 0 0
"""


MEMORY_OUTPUT = """\
              total        used        free      shared  buff/cache   available
Mem:     8000000000  4000000000  2000000000   100000000   2000000000  3500000000
Swap:    2000000000           0  2000000000
"""


DISK_OUTPUT = """\
Filesystem     1024-blocks     Used Available Capacity Mounted on
/dev/sda1          100000000 50000000 50000000      50% /
"""


def test_check_host_ok():
    execute = create_command_responses(
        CPU_OUTPUT,
        MEMORY_OUTPUT,
        DISK_OUTPUT,
    )

    result = check_host(
        "server01",
        execute,
    )

    assert result.host == "server01"
    assert result.status == HealthStatus.OK

    assert result.metrics.cpu == 35.0
    assert result.metrics.memory == 50.0
    assert result.metrics.disk == 50.0

    assert result.cpu_status == HealthStatus.OK
    assert result.memory_status == HealthStatus.OK
    assert result.disk_status == HealthStatus.OK

    assert result.error is None


def test_check_host_connection_error():
    def failing_execute(command):
        raise TimeoutError(
            "Timeout ao executar comando"
        )

    result = check_host(
        "server01",
        failing_execute,
    )

    assert result.host == "server01"
    assert result.status == HealthStatus.CONNECTION_ERROR
    assert result.error == "Timeout ao executar comando"
    assert result.metrics is None


def test_check_host_invalid_response():
    def invalid_execute(command):
        return {
            "stdout": "resposta inválida",
            "stderr": "",
            "exit_code": 0,
        }

    result = check_host(
        "server01",
        invalid_execute,
    )

    assert result.status == HealthStatus.CONNECTION_ERROR
    assert result.error is not None

def test_check_host_cpu_critical():
    cpu_output = """\
cpu  100 20 30 850 0 0 0 0 0 0 0
cpu  200 30 70 850 0 0 0 0 0 0 0
"""

    execute = create_command_responses(
        cpu_output,
        MEMORY_OUTPUT,
        DISK_OUTPUT,
    )

    result = check_host(
        "server01",
        execute,
    )

    assert result.cpu_status == HealthStatus.CRITICAL
    assert result.status == HealthStatus.CRITICAL

def test_run_healthchecks_with_fake_ssh():
    from infra_cli.healthcheck import run_healthchecks

    class FakeSSHClient:
        def __init__(self, hostname, username, port):
            self.hostname = hostname
            self.username = username
            self.port = port
            self.connected = False
            self.closed = False

        def connect(self, passphrase=None):
            self.connected = True

        def execute(self, command):
            if "/proc/stat" in command:
                return {
                    "stdout": CPU_OUTPUT,
                    "stderr": "",
                    "exit_code": 0,
                }

            if command == "free -b":
                return {
                    "stdout": MEMORY_OUTPUT,
                    "stderr": "",
                    "exit_code": 0,
                }

            if command == "df -P /":
                return {
                    "stdout": DISK_OUTPUT,
                    "stderr": "",
                    "exit_code": 0,
                }

            raise AssertionError(
                f"Comando inesperado: {command}"
            )

        def close(self):
            self.closed = True

    servers = [
        {
            "name": "server01",
            "hostname": "192.168.1.101",
            "username": "ubuntu",
            "port": 22,
        }
    ]

    results = run_healthchecks(
        servers,
        "test-passphrase",
        FakeSSHClient,
    )

    assert len(results) == 1
    assert results[0].host == "server01"
    assert results[0].status == HealthStatus.OK

def test_run_healthchecks_ssh_failure():
    from infra_cli.healthcheck import run_healthchecks

    class FailingSSHClient:
        def __init__(self, hostname, username, port):
            pass

        def connect(self, passphrase=None):
            raise ConnectionError(
                "Timeout ao conectar ao host server01"
            )

        def close(self):
            pass

    servers = [
        {
            "name": "server01",
            "hostname": "192.168.1.101",
            "username": "ubuntu",
            "port": 22,
        }
    ]

    results = run_healthchecks(
        servers,
        "test-passphrase",
        FailingSSHClient,
    )

    assert len(results) == 1
    assert results[0].host == "server01"
    assert results[0].status == HealthStatus.CONNECTION_ERROR
    assert (
        results[0].error
        == "Timeout ao conectar ao host server01"
    )
