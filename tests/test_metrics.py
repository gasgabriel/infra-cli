import pytest

from infra_cli.metrics import (
    ServerMetrics,
    get_cpu_usage,
    get_disk_usage,
    get_memory_usage,
    parse_cpu_stat,
    parse_disk,
    parse_memory,
)


def test_server_metrics():
    metrics = ServerMetrics(
        cpu=25.0,
        memory=40.0,
        disk=50.0,
    )

    assert metrics.cpu == 25.0
    assert metrics.memory == 40.0
    assert metrics.disk == 50.0


def test_parse_cpu_stat():
    output = """\
cpu  100 20 30 850 0 0 0 0 0 0 0
cpu  120 25 40 915 0 0 0 0 0 0 0
"""

    result = parse_cpu_stat(output)

    assert result == 35.0


def test_parse_cpu_stat_invalid_number_of_samples():
    output = """\
cpu  100 20 30 850 0 0 0 0 0 0 0
"""

    with pytest.raises(ValueError, match="Resposta de CPU inválida"):
        parse_cpu_stat(output)


def test_parse_cpu_stat_invalid_format():
    output = """\
foo 100 20 30 850
foo 120 25 40 915
"""

    with pytest.raises(
        ValueError,
        match="Formato de /proc/stat inválido",
    ):
        parse_cpu_stat(output)


def test_parse_cpu_stat_insufficient_data():
    output = """\
cpu 100 20 30
cpu 120 25 40
"""

    with pytest.raises(
        ValueError,
        match="Dados de CPU insuficientes",
    ):
        parse_cpu_stat(output)


def test_parse_memory():
    output = """\
              total        used        free      shared  buff/cache   available
Mem:     8000000000  4000000000  2000000000   100000000   2000000000  3500000000
Swap:    2000000000           0  2000000000
"""

    result = parse_memory(output)

    assert result == 50.0


def test_parse_memory_invalid():
    output = """\
Swap: 2000000000 0 2000000000
"""

    with pytest.raises(
        ValueError,
        match="Resposta de memória inválida",
    ):
        parse_memory(output)


def test_parse_memory_invalid_total():
    output = """\
Mem: 0 0 0
"""

    with pytest.raises(
        ValueError,
        match="Memória total inválida",
    ):
        parse_memory(output)


def test_parse_disk():
    output = """\
Filesystem     1024-blocks     Used Available Capacity Mounted on
/dev/sda1          100000000 50000000 50000000      50% /
"""

    result = parse_disk(output)

    assert result == 50.0


def test_parse_disk_invalid():
    output = """\
Filesystem     1024-blocks     Used Available Capacity Mounted on
/dev/sda1          100000000 50000000 50000000      50 /
"""

    with pytest.raises(
        ValueError,
        match="Percentual de disco inválido",
    ):
        parse_disk(output)


def test_get_cpu_usage():
    output = """\
cpu  100 20 30 850 0 0 0 0 0 0 0
cpu  120 25 40 915 0 0 0 0 0 0 0
"""

    def fake_execute(command):
        return {
            "stdout": output,
            "stderr": "",
            "exit_code": 0,
        }

    result = get_cpu_usage(fake_execute)

    assert result == 35.0


def test_get_cpu_usage_command_failure():
    def fake_execute(command):
        return {
            "stdout": "",
            "stderr": "permission denied",
            "exit_code": 1,
        }

    with pytest.raises(RuntimeError, match="permission denied"):
        get_cpu_usage(fake_execute)


def test_get_memory_usage():
    output = """\
              total        used        free      shared  buff/cache   available
Mem:     8000000000  4000000000  2000000000   100000000   2000000000  3500000000
Swap:    2000000000           0  2000000000
"""

    def fake_execute(command):
        return {
            "stdout": output,
            "stderr": "",
            "exit_code": 0,
        }

    result = get_memory_usage(fake_execute)

    assert result == 50.0


def test_get_disk_usage():
    output = """\
Filesystem     1024-blocks     Used Available Capacity Mounted on
/dev/sda1          100000000 50000000 50000000      50% /
"""

    def fake_execute(command):
        return {
            "stdout": output,
            "stderr": "",
            "exit_code": 0,
        }

    result = get_disk_usage(fake_execute)

    assert result == 50.0

def test_parse_cpu_stat_invalid_interval():
    output = (
        "cpu 100 0 0 100 0 0 0 0 0 0 0\n"
        "cpu 100 0 0 100 0 0 0 0 0 0 0\n"
    )

    with pytest.raises(
        ValueError,
        match="Intervalo de CPU inválido",
    ):
        parse_cpu_stat(output)


def test_parse_memory_insufficient_data():
    output = "Mem: 1000\n"

    with pytest.raises(
        ValueError,
        match="Dados de memória insuficientes",
    ):
        parse_memory(output)


def test_parse_disk_invalid_response():
    output = "Filesystem\n"

    with pytest.raises(
        ValueError,
        match="Resposta de disco inválida",
    ):
        parse_disk(output)


def test_parse_disk_insufficient_data():
    output = (
        "Filesystem Size Used Avail Use% Mounted\n"
        "/dev/sda1 100G 50G 50G\n"
    )

    with pytest.raises(
        ValueError,
        match="Dados de disco insuficientes",
    ):
        parse_disk(output)


def test_parse_disk_invalid_value():
    output = (
        "Filesystem Size Used Avail Use% Mounted\n"
        "/dev/sda1 100G 50G 50G abc% /\n"
    )

    with pytest.raises(
        ValueError,
        match="Valor de disco inválido",
    ):
        parse_disk(output)


def test_get_disk_usage_command_failure():
    def execute_command(command):
        return {
            "exit_code": 1,
            "stdout": "",
            "stderr": "Erro ao executar df.",
        }

    with pytest.raises(
        RuntimeError,
        match="Erro ao executar df.",
    ):
        get_disk_usage(execute_command)


def test_get_disk_usage_command_failure_without_stderr():
    def execute_command(command):
        return {
            "exit_code": 1,
            "stdout": "",
            "stderr": "",
        }

    with pytest.raises(
        RuntimeError,
        match="Falha ao coletar disco",
    ):
        get_disk_usage(execute_command)
