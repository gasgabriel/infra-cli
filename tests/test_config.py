
import pytest

from infra_cli.config import ConfigError, load_hosts


def test_load_hosts_success(tmp_path):
    config_file = tmp_path / "hosts.yaml"

    config_file.write_text(
        """
hosts:
  - name: server01
    hostname: 192.168.1.101
    port: 22
  - name: server03
    hostname: 192.168.1.103
    port: 2222
""",
        encoding="utf-8",
    )

    result = load_hosts(str(config_file))

    assert result == [
        {
            "name": "server01",
            "hostname": "192.168.1.101",
            "port": 22,
        },
        {
            "name": "server03",
            "hostname": "192.168.1.103",
            "port": 2222,
        },
    ]


def test_load_hosts_file_not_found(tmp_path):
    config_file = tmp_path / "inexistente.yaml"

    with pytest.raises(
        ConfigError,
        match="Arquivo de configuração não encontrado",
    ):
        load_hosts(str(config_file))


def test_load_hosts_invalid_yaml(tmp_path):
    config_file = tmp_path / "invalid.yaml"

    config_file.write_text(
        """
hosts:
  - name: server01
    hostname: [192.168.1.101
""",
        encoding="utf-8",
    )

    with pytest.raises(
        ConfigError,
        match="Erro ao interpretar o arquivo YAML",
    ):
        load_hosts(str(config_file))


def test_load_hosts_root_not_object(tmp_path):
    config_file = tmp_path / "invalid-root.yaml"

    config_file.write_text(
        """
- server01
- server03
""",
        encoding="utf-8",
    )

    with pytest.raises(
        ConfigError,
        match="A configuração deve ser um objeto YAML",
    ):
        load_hosts(str(config_file))


def test_load_hosts_without_hosts_key(tmp_path):
    config_file = tmp_path / "missing-hosts.yaml"

    config_file.write_text(
        """
servers:
  - name: server01
""",
        encoding="utf-8",
    )

    with pytest.raises(
        ConfigError,
        match="A configuração deve conter uma lista 'hosts'",
    ):
        load_hosts(str(config_file))


def test_load_hosts_hosts_is_not_list(tmp_path):
    config_file = tmp_path / "invalid-hosts.yaml"

    config_file.write_text(
        """
hosts:
  server01:
    hostname: 192.168.1.101
""",
        encoding="utf-8",
    )

    with pytest.raises(
        ConfigError,
        match="A configuração deve conter uma lista 'hosts'",
    ):
        load_hosts(str(config_file))

