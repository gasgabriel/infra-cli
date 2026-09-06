import click
from pathlib import Path

from infra_cli.alerts import generate_alerts
from infra_cli.config import ConfigError, load_hosts
from infra_cli.webhook import WebhookError, send_alerts

from .healthcheck import run_healthchecks
from .health_rules import HealthStatus
from .report import generate_html, generate_json


@click.group()
def cli():
    """Ferramenta de automação e monitoramento de infraestrutura."""
    pass


def load_servers(host: str | None = None) -> list[dict]:
    """Carrega os servidores configurados e aplica filtro opcional."""

    try:
        servers = load_hosts()
    except ConfigError as exc:
        raise click.ClickException(str(exc)) from exc

    if host:
        servers = [
            server
            for server in servers
            if server["name"] == host
        ]

        if not servers:
            raise click.ClickException(
                f"Servidor '{host}' não encontrado na configuração."
            )

    return servers


@cli.command()
def hosts():
    """Lista os servidores configurados."""

    try:
        servers = load_hosts()
    except ConfigError as exc:
        raise click.ClickException(str(exc)) from exc

    click.echo("Servidores configurados:")
    click.echo()

    for server in servers:
        click.echo(
            f"{server['name']} → "
            f"{server['hostname']}:{server['port']}"
        )


@cli.command()
@click.option(
    "--format",
    "output_format",
    type=click.Choice(
        ["json", "html"],
        case_sensitive=False,
    ),
    default="json",
    show_default=True,
    help="Formato do relatório.",
)
@click.option(
    "--host",
    help="Gera o relatório de um servidor específico.",
)
def report(output_format, host):
    """Gera relatórios de infraestrutura."""

    from infra_cli.ssh import SSHClient

    servers = load_servers(host)

    passphrase = click.prompt(
        "Passphrase da chave SSH",
        hide_input=True,
    )

    results = run_healthchecks(
        servers,
        passphrase,
        SSHClient,
    )

    output_format = output_format.lower()

    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)

    if output_format == "json":
        content = generate_json(results)
        output_file = reports_dir / "health-report.json"

    else:
        template_dir = Path("templates")

        content = generate_html(
            results,
            template_dir,
        )

        output_file = reports_dir / "health-report.html"

    output_file.write_text(
        content,
        encoding="utf-8",
    )

    click.echo(
        f"Relatório gerado: {output_file}"
    )


@cli.command()
def alert():
    """Gerencia alertas de infraestrutura."""

    click.echo(
        "Os alertas são gerados automaticamente durante o healthcheck."
    )


@cli.command()
@click.option(
    "--host",
    help="Executa o healthcheck em um servidor específico.",
)

@click.option(
    "--no-alert",
    is_flag=True,
    default=False,
    help="Executa o healthcheck sem enviar alertas pelo webhook.",
)

def healthcheck(host, no_alert):
    """Executa verificações de saúde dos servidores."""

    from infra_cli.ssh import SSHClient

    servers = load_servers(host)

    passphrase = click.prompt(
        "Passphrase da chave SSH",
        hide_input=True,
    )

    results = run_healthchecks(
        servers,
        passphrase,
        SSHClient,
    )

    # ========================================
    # 1. Exibe os resultados dos servidores
    # ========================================

    for result in results:
        click.echo()
        click.echo(f"Servidor: {result.host}")
        click.echo("-" * 40)

        if result.error:
            click.echo(
                f"Status: {result.status.value}"
            )

            click.echo(
                f"ERRO: {result.error}"
            )

            continue

        click.echo(
            f"CPU:      {result.metrics.cpu:.2f}% "
            f"[{result.cpu_status.value}]"
        )

        click.echo(
            f"Memória:  {result.metrics.memory:.2f}% "
            f"[{result.memory_status.value}]"
        )

        click.echo(
            f"Disco:    {result.metrics.disk:.2f}% "
            f"[{result.disk_status.value}]"
        )

        click.echo()

        click.echo(
            f"Status geral: {result.status.value}"
        )

    # ========================================
    # 2. Gera os alertas
    # ========================================

    alerts = generate_alerts(results)

    # ========================================
    # 3. Exibe os alertas na tela
    # ========================================

    if alerts:
        click.echo()
        click.echo("ALERTAS")
        click.echo("=" * 40)

        for alert in alerts:
            click.echo(
                f"[{alert.severity}] "
                f"{alert.host} - "
                f"{alert.metric}: "
                f"{alert.message}"
            )
    else:
        click.echo()
        click.echo("Nenhum alerta detectado.")

    # ========================================
    # 4. Envia os alertas para o webhook
    # ========================================

    if alerts: 
        if no_alert:
            click.echo()
            click.echo(
                "Envio de alertas desativado "
                "pela opção --no-alert."  
            )

        else:
            try:
                webhook_configured = send_alerts(alerts)

                if webhook_configured:
                    click.echo()
                    click.echo(
                        f"{len(alerts)} alerta(s) enviado(s) "
                        "para o webhook."
                    )
                else:
                    click.echo()
                    click.echo(
                        "Webhook não configurado. "
                        "Alertas não enviados."
                    )

            except WebhookError as exc:
                click.echo()
                click.echo(
                    f"Aviso: {exc}",
                    err=True,
                )

    # ========================================
    # 5. Finaliza o healthcheck
    # ========================================

    click.echo()
    click.echo("Healthcheck concluído.")

    # ========================================
    # 6. Exit code operacional
    # ========================================

    if any(
        result.status != HealthStatus.OK
        for result in results
    ):
        raise click.exceptions.Exit(1)


@cli.command()
@click.option("--host", required=True, help="Host remoto.")
@click.option("--user", required=True, help="Usuário SSH.")
def ssh_test(host: str, user: str):
    """Testa a conectividade SSH com um servidor."""

    from infra_cli.ssh import SSHClient

    click.echo(f"Conectando {host}...", nl=False)

    client = SSHClient(
        hostname=host,
        username=user,
    )

    try:
        client.connect()
        click.echo(" OK")

    except ConnectionError as exc:
        click.echo(" ERROR")
        click.echo(str(exc))

    finally:
        client.close()


if __name__ == "__main__":
    cli()
