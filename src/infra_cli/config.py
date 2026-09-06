from pathlib import Path

import yaml


class ConfigError(Exception):
    """Erro relacionado à configuração da aplicação."""


def load_hosts(config_path: str = "hosts.yaml") -> list[dict]:
    """Carrega os servidores definidos no arquivo YAML."""

    path = Path(config_path)

    if not path.exists():
        raise ConfigError(
            f"Arquivo de configuração não encontrado: {path}"
        )

    try:
        with path.open("r", encoding="utf-8") as file:
            config = yaml.safe_load(file)
    except yaml.YAMLError as exc:
        raise ConfigError(
            f"Erro ao interpretar o arquivo YAML: {path}"
        ) from exc

    if not isinstance(config, dict):
        raise ConfigError("A configuração deve ser um objeto YAML.")

    hosts = config.get("hosts")

    if not isinstance(hosts, list):
        raise ConfigError(
            "A configuração deve conter uma lista 'hosts'."
        )

    return hosts
