from dataclasses import dataclass


@dataclass
class ServerMetrics:
    """Métricas coletadas de um servidor Linux."""

    cpu: float
    memory: float
    disk: float


def parse_cpu_stat(output: str) -> float:
    """Calcula o percentual de uso da CPU a partir de duas amostras."""

    lines = [
        line.strip()
        for line in output.splitlines()
        if line.strip()
    ]

    if len(lines) != 2:
        raise ValueError("Resposta de CPU inválida.")

    samples = []

    for line in lines:
        parts = line.split()

        if parts[0] != "cpu":
            raise ValueError("Formato de /proc/stat inválido.")

        values = [int(value) for value in parts[1:]]

        if len(values) < 4:
            raise ValueError("Dados de CPU insuficientes.")

        idle = values[3]
        total = sum(values)

        samples.append((total, idle))

    total_1, idle_1 = samples[0]
    total_2, idle_2 = samples[1]

    total_delta = total_2 - total_1
    idle_delta = idle_2 - idle_1

    if total_delta <= 0:
        raise ValueError("Intervalo de CPU inválido.")

    usage = (1 - idle_delta / total_delta) * 100

    return round(usage, 2)


def get_cpu_usage(execute_command) -> float:
    """Obtém o uso da CPU no servidor remoto."""

    command = """
read cpu user nice system idle iowait irq softirq steal guest guest_nice < /proc/stat
echo "$cpu $user $nice $system $idle $iowait $irq $softirq $steal $guest $guest_nice"
sleep 1
read cpu user nice system idle iowait irq softirq steal guest guest_nice < /proc/stat
echo "$cpu $user $nice $system $idle $iowait $irq $softirq $steal $guest $guest_nice"
"""

    result = execute_command(command)

    if result["exit_code"] != 0:
        raise RuntimeError(
            result["stderr"].strip() or "Falha ao coletar CPU."
        )

    return parse_cpu_stat(result["stdout"])


def parse_memory(output: str) -> float:
    """Calcula o percentual de memória utilizada."""

    lines = [
        line.split()
        for line in output.splitlines()
    ]

    memory_line = next(
        (line for line in lines if line and line[0] == "Mem:"),
        None,
    )

    if memory_line is None:
        raise ValueError("Resposta de memória inválida.")

    if len(memory_line) < 3:
        raise ValueError("Dados de memória insuficientes.")

    total = int(memory_line[1])
    used = int(memory_line[2])

    if total <= 0:
        raise ValueError("Memória total inválida.")

    usage = (used / total) * 100

    return round(usage, 2)


def get_memory_usage(execute_command) -> float:
    """Obtém o percentual de memória utilizada."""

    result = execute_command("free -b")

    if result["exit_code"] != 0:
        raise RuntimeError(
            result["stderr"].strip() or "Falha ao coletar memória."
        )

    return parse_memory(result["stdout"])


def parse_disk(output: str) -> float:
    """Extrai o percentual de utilização do disco raiz."""

    lines = [
        line.split()
        for line in output.splitlines()
        if line.strip()
    ]

    if len(lines) < 2:
        raise ValueError("Resposta de disco inválida.")

    data = lines[-1]

    if len(data) < 5:
        raise ValueError("Dados de disco insuficientes.")

    usage = data[4]

    if not usage.endswith("%"):
        raise ValueError("Percentual de disco inválido.")

    try:
        value = float(usage.rstrip("%"))
    except ValueError as exc:
        raise ValueError("Valor de disco inválido.") from exc

    return value


def get_disk_usage(execute_command) -> float:
    """Obtém o percentual de utilização do disco raiz."""

    result = execute_command("df -P /")

    if result["exit_code"] != 0:
        raise RuntimeError(
            result["stderr"].strip() or "Falha ao coletar disco."
        )

    return parse_disk(result["stdout"])
