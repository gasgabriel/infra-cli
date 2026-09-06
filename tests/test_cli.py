from types import SimpleNamespace

from click.testing import CliRunner

from infra_cli.cli import cli, load_servers
from infra_cli.config import ConfigError
from infra_cli.health_rules import HealthStatus


def test_cli_help():
    runner = CliRunner()

    result = runner.invoke(cli, ["--help"])

    assert result.exit_code == 0
    assert "Ferramenta de automação e monitoramento de infraestrutura." in result.output
    assert "healthcheck" in result.output
    assert "hosts" in result.output
    assert "report" in result.output
    assert "ssh-test" in result.output


def test_load_servers_returns_all(monkeypatch):
    servers = [
        {
            "name": "server01",
            "hostname": "192.168.1.101",
            "port": 22,
        },
        {
            "name": "server03",
            "hostname": "192.168.1.103",
            "port": 22,
        },
    ]

    monkeypatch.setattr(
        "infra_cli.cli.load_hosts",
        lambda: servers,
    )

    result = load_servers()

    assert result == servers


def test_load_servers_filters_host(monkeypatch):
    servers = [
        {
            "name": "server01",
            "hostname": "192.168.1.101",
            "port": 22,
        },
        {
            "name": "server03",
            "hostname": "192.168.1.103",
            "port": 22,
        },
    ]

    monkeypatch.setattr(
        "infra_cli.cli.load_hosts",
        lambda: servers,
    )

    result = load_servers("server03")

    assert result == [servers[1]]


def test_load_servers_unknown_host(monkeypatch):
    monkeypatch.setattr(
        "infra_cli.cli.load_hosts",
        lambda: [],
    )

    runner = CliRunner()

    result = runner.invoke(cli, ["healthcheck", "--host", "unknown"])

    assert result.exit_code != 0
    assert "Servidor 'unknown' não encontrado na configuração." in result.output


def test_load_servers_config_error(monkeypatch):
    def fake_load_hosts():
        raise ConfigError("Configuração inválida.")

    monkeypatch.setattr(
        "infra_cli.cli.load_hosts",
        fake_load_hosts,
    )

    runner = CliRunner()

    result = runner.invoke(cli, ["hosts"])

    assert result.exit_code != 0
    assert "Configuração inválida." in result.output


def test_hosts_command(monkeypatch):
    servers = [
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

    monkeypatch.setattr(
        "infra_cli.cli.load_hosts",
        lambda: servers,
    )

    runner = CliRunner()

    result = runner.invoke(cli, ["hosts"])

    assert result.exit_code == 0
    assert "Servidores configurados:" in result.output
    assert "server01 → 192.168.1.101:22" in result.output
    assert "server03 → 192.168.1.103:2222" in result.output


def test_alert_command():
    runner = CliRunner()

    result = runner.invoke(cli, ["alert"])

    assert result.exit_code == 0
    assert "Os alertas são gerados automaticamente" in result.output


def test_healthcheck_ok_without_alerts(monkeypatch):
    servers = [
        {
            "name": "server01",
            "hostname": "192.168.1.101",
            "port": 22,
        }
    ]

    metrics = SimpleNamespace(
        cpu=20.0,
        memory=30.0,
        disk=40.0,
    )

    result = SimpleNamespace(
        host="server01",
        metrics=metrics,
        cpu_status=HealthStatus.OK,
        memory_status=HealthStatus.OK,
        disk_status=HealthStatus.OK,
        status=HealthStatus.OK,
        error=None,
    )

    monkeypatch.setattr(
        "infra_cli.cli.load_hosts",
        lambda: servers,
    )

    monkeypatch.setattr(
        "infra_cli.cli.run_healthchecks",
        lambda servers, passphrase, ssh_client: [result],
    )

    monkeypatch.setattr(
        "infra_cli.cli.generate_alerts",
        lambda results: [],
    )

    monkeypatch.setattr(
        "infra_cli.cli.send_alerts",
        lambda alerts: True,
    )

    runner = CliRunner()

    result_cli = runner.invoke(
        cli,
        ["healthcheck"],
        input="senha-teste\n",
    )

    assert result_cli.exit_code == 0
    assert "Servidor: server01" in result_cli.output
    assert "CPU:      20.00% [OK]" in result_cli.output
    assert "Memória:  30.00% [OK]" in result_cli.output
    assert "Disco:    40.00% [OK]" in result_cli.output
    assert "Status geral: OK" in result_cli.output
    assert "Nenhum alerta detectado." in result_cli.output
    assert "Healthcheck concluído." in result_cli.output


def test_healthcheck_with_no_alert_option(monkeypatch):
    servers = [
        {
            "name": "server01",
            "hostname": "192.168.1.101",
            "port": 22,
        }
    ]

    metrics = SimpleNamespace(
        cpu=95.0,
        memory=30.0,
        disk=40.0,
    )

    health_result = SimpleNamespace(
        host="server01",
        metrics=metrics,
        cpu_status=HealthStatus.CRITICAL,
        memory_status=HealthStatus.OK,
        disk_status=HealthStatus.OK,
        status=HealthStatus.CRITICAL,
        error=None,
    )

    alert = SimpleNamespace(
        severity="CRITICAL",
        host="server01",
        metric="CPU",
        message="CPU acima do limite crítico.",
    )

    monkeypatch.setattr(
        "infra_cli.cli.load_hosts",
        lambda: servers,
    )

    monkeypatch.setattr(
        "infra_cli.cli.run_healthchecks",
        lambda servers, passphrase, ssh_client: [health_result],
    )

    monkeypatch.setattr(
        "infra_cli.cli.generate_alerts",
        lambda results: [alert],
    )

    send_called = False

    def fake_send_alerts(alerts):
        nonlocal send_called
        send_called = True
        return True

    monkeypatch.setattr(
        "infra_cli.cli.send_alerts",
        fake_send_alerts,
    )

    runner = CliRunner()

    result_cli = runner.invoke(
        cli,
        ["healthcheck", "--no-alert"],
        input="senha-teste\n",
    )

    assert result_cli.exit_code == 1
    assert "[CRITICAL] server01 - CPU" in result_cli.output
    assert "Envio de alertas desativado pela opção --no-alert." in result_cli.output
    assert send_called is False


def test_healthcheck_webhook_not_configured(monkeypatch):
    servers = [
        {
            "name": "server01",
            "hostname": "192.168.1.101",
            "port": 22,
        }
    ]

    health_result = SimpleNamespace(
        host="server01",
        metrics=SimpleNamespace(
            cpu=95.0,
            memory=30.0,
            disk=40.0,
        ),
        cpu_status=HealthStatus.CRITICAL,
        memory_status=HealthStatus.OK,
        disk_status=HealthStatus.OK,
        status=HealthStatus.CRITICAL,
        error=None,
    )

    alert = SimpleNamespace(
        severity="CRITICAL",
        host="server01",
        metric="CPU",
        message="CPU acima do limite crítico.",
    )

    monkeypatch.setattr(
        "infra_cli.cli.load_hosts",
        lambda: servers,
    )

    monkeypatch.setattr(
        "infra_cli.cli.run_healthchecks",
        lambda servers, passphrase, ssh_client: [health_result],
    )

    monkeypatch.setattr(
        "infra_cli.cli.generate_alerts",
        lambda results: [alert],
    )

    monkeypatch.setattr(
        "infra_cli.cli.send_alerts",
        lambda alerts: False,
    )

    runner = CliRunner()

    result_cli = runner.invoke(
        cli,
        ["healthcheck"],
        input="senha-teste\n",
    )

    assert result_cli.exit_code == 1
    assert "Webhook não configurado. Alertas não enviados." in result_cli.output
    assert "Healthcheck concluído." in result_cli.output


def test_healthcheck_webhook_error(monkeypatch):
    servers = [
        {
            "name": "server01",
            "hostname": "192.168.1.101",
            "port": 22,
        }
    ]

    health_result = SimpleNamespace(
        host="server01",
        metrics=SimpleNamespace(
            cpu=95.0,
            memory=30.0,
            disk=40.0,
        ),
        cpu_status=HealthStatus.CRITICAL,
        memory_status=HealthStatus.OK,
        disk_status=HealthStatus.OK,
        status=HealthStatus.CRITICAL,
        error=None,
    )

    alert = SimpleNamespace(
        severity="CRITICAL",
        host="server01",
        metric="CPU",
        message="CPU acima do limite crítico.",
    )

    monkeypatch.setattr(
        "infra_cli.cli.load_hosts",
        lambda: servers,
    )

    monkeypatch.setattr(
        "infra_cli.cli.run_healthchecks",
        lambda servers, passphrase, ssh_client: [health_result],
    )

    monkeypatch.setattr(
        "infra_cli.cli.generate_alerts",
        lambda results: [alert],
    )

    def fake_send_alerts(alerts):
        from infra_cli.webhook import WebhookError

        raise WebhookError("Falha ao enviar webhook.")

    monkeypatch.setattr(
        "infra_cli.cli.send_alerts",
        fake_send_alerts,
    )

    runner = CliRunner()

    result_cli = runner.invoke(
        cli,
        ["healthcheck"],
        input="senha-teste\n",
    )

    assert result_cli.exit_code == 1
    assert "Aviso: Falha ao enviar webhook." in result_cli.output
    assert "Healthcheck concluído." in result_cli.output


def test_healthcheck_connection_error_result(monkeypatch):
    servers = [
        {
            "name": "server01",
            "hostname": "192.168.1.101",
            "port": 22,
        }
    ]

    health_result = SimpleNamespace(
        host="server01",
        metrics=None,
        cpu_status=None,
        memory_status=None,
        disk_status=None,
        status=HealthStatus.CONNECTION_ERROR,
        error="Timeout ao conectar ao host.",
    )

    monkeypatch.setattr(
        "infra_cli.cli.load_hosts",
        lambda: servers,
    )

    monkeypatch.setattr(
        "infra_cli.cli.run_healthchecks",
        lambda servers, passphrase, ssh_client: [health_result],
    )

    monkeypatch.setattr(
        "infra_cli.cli.generate_alerts",
        lambda results: [],
    )

    runner = CliRunner()

    result_cli = runner.invoke(
        cli,
        ["healthcheck", "--no-alert"],
        input="senha-teste\n",
    )

    assert result_cli.exit_code == 1
    assert "Status: CONNECTION_ERROR" in result_cli.output
    assert "ERRO: Timeout ao conectar ao host." in result_cli.output
    assert "Healthcheck concluído." in result_cli.output


def test_report_json(monkeypatch, tmp_path):
    servers = [
        {
            "name": "server01",
            "hostname": "192.168.1.101",
            "port": 22,
        }
    ]

    monkeypatch.chdir(tmp_path)

    monkeypatch.setattr(
        "infra_cli.cli.load_hosts",
        lambda: servers,
    )

    fake_results = ["resultado-teste"]

    monkeypatch.setattr(
        "infra_cli.cli.run_healthchecks",
        lambda servers, passphrase, ssh_client: fake_results,
    )

    monkeypatch.setattr(
        "infra_cli.cli.generate_json",
        lambda results: '{"status": "ok"}',
    )

    runner = CliRunner()

    result = runner.invoke(
        cli,
        ["report", "--format", "json"],
        input="senha-teste\n",
    )

    assert result.exit_code == 0
    assert "Relatório gerado: reports/health-report.json" in result.output

    report_file = tmp_path / "reports" / "health-report.json"

    assert report_file.exists()
    assert report_file.read_text(encoding="utf-8") == '{"status": "ok"}'


def test_report_html(monkeypatch, tmp_path):
    servers = [
        {
            "name": "server01",
            "hostname": "192.168.1.101",
            "port": 22,
        }
    ]

    monkeypatch.chdir(tmp_path)

    monkeypatch.setattr(
        "infra_cli.cli.load_hosts",
        lambda: servers,
    )

    monkeypatch.setattr(
        "infra_cli.cli.run_healthchecks",
        lambda servers, passphrase, ssh_client: ["resultado"],
    )

    monkeypatch.setattr(
        "infra_cli.cli.generate_html",
        lambda results, template_dir: "<html>teste</html>",
    )

    runner = CliRunner()

    result = runner.invoke(
        cli,
        ["report", "--format", "html"],
        input="senha-teste\n",
    )

    assert result.exit_code == 0
    assert "Relatório gerado: reports/health-report.html" in result.output

    report_file = tmp_path / "reports" / "health-report.html"

    assert report_file.exists()
    assert report_file.read_text(encoding="utf-8") == "<html>teste</html>"


def test_report_invalid_format():
    runner = CliRunner()

    result = runner.invoke(
        cli,
        ["report", "--format", "xml"],
    )

    assert result.exit_code != 0
    assert "Invalid value for '--format'" in result.output


def test_ssh_test_success(monkeypatch):
    class FakeSSHClient:
        def __init__(self, hostname, username):
            self.hostname = hostname
            self.username = username
            self.connected = False
            self.closed = False

        def connect(self):
            self.connected = True

        def close(self):
            self.closed = True

    monkeypatch.setattr(
        "infra_cli.ssh.SSHClient",
        FakeSSHClient,
    )

    runner = CliRunner()

    result = runner.invoke(
        cli,
        [
            "ssh-test",
            "--host",
            "192.168.1.101",
            "--user",
            "ubuntu",
        ],
    )

    assert result.exit_code == 0
    assert "Conectando 192.168.1.101... OK" in result.output


def test_ssh_test_connection_error(monkeypatch):
    class FakeSSHClient:
        def __init__(self, hostname, username):
            self.hostname = hostname
            self.username = username

        def connect(self):
            raise ConnectionError("Timeout de conexão.")

        def close(self):
            pass

    monkeypatch.setattr(
        "infra_cli.ssh.SSHClient",
        FakeSSHClient,
    )

    runner = CliRunner()

    result = runner.invoke(
        cli,
        [
            "ssh-test",
            "--host",
            "192.168.1.101",
            "--user",
            "ubuntu",
        ],
    )

    assert result.exit_code == 0
    assert "Conectando 192.168.1.101... ERROR" in result.output
    assert "Timeout de conexão." in result.output
