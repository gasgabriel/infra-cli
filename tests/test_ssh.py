import paramiko
import pytest

from infra_cli.ssh import SSHClient


def test_ssh_client_defaults():
    client = SSHClient(
        hostname="server01",
        username="ubuntu",
    )

    assert client.hostname == "server01"
    assert client.username == "ubuntu"
    assert client.port == 22
    assert client.timeout == 10

    client.close()


def test_ssh_authentication_error(monkeypatch):
    client = SSHClient(
        hostname="server01",
        username="ubuntu",
    )

    def fake_connect(**kwargs):
        raise paramiko.AuthenticationException()

    monkeypatch.setattr(
        client.client,
        "connect",
        fake_connect,
    )

    with pytest.raises(
        ConnectionError,
        match="Falha de autenticação",
    ):
        client.connect()

    client.close()


def test_ssh_error(monkeypatch):
    client = SSHClient(
        hostname="server01",
        username="ubuntu",
    )

    def fake_connect(**kwargs):
        raise paramiko.SSHException()

    monkeypatch.setattr(
        client.client,
        "connect",
        fake_connect,
    )

    with pytest.raises(
        ConnectionError,
        match="Erro SSH ao conectar",
    ):
        client.connect()

    client.close()


def test_ssh_timeout(monkeypatch):
    client = SSHClient(
        hostname="server01",
        username="ubuntu",
    )

    def fake_connect(**kwargs):
        raise TimeoutError()

    monkeypatch.setattr(
        client.client,
        "connect",
        fake_connect,
    )

    with pytest.raises(
        ConnectionError,
        match="Timeout ao conectar",
    ):
        client.connect()

    client.close()


def test_ssh_network_error(monkeypatch):
    client = SSHClient(
        hostname="server01",
        username="ubuntu",
    )

    def fake_connect(**kwargs):
        raise OSError()

    monkeypatch.setattr(
        client.client,
        "connect",
        fake_connect,
    )

    with pytest.raises(
        ConnectionError,
        match="Erro de rede ao conectar",
    ):
        client.connect()

    client.close()

def test_ssh_uses_reject_policy():
    client = SSHClient(
        hostname="server01",
        username="ubuntu",
    )

    assert isinstance(
        client.client._policy,
        paramiko.RejectPolicy,
    )

    client.close()
