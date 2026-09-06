import json
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from .healthcheck import HealthcheckResult


class ReportError(Exception):
    """Erro relacionado à geração de relatórios."""


def result_to_dict(result: HealthcheckResult) -> dict:
    """Converte um resultado de healthcheck em um dicionário."""

    if result.error:
        return {
            "host": result.host,
            "cpu": None,
            "memory": None,
            "disk": None,
            "status": result.status.value,
            "error": result.error,
        }

    return {
        "host": result.host,
        "cpu": result.metrics.cpu,
        "memory": result.metrics.memory,
        "disk": result.metrics.disk,
        "status": result.status.value,
        "cpu_status": result.cpu_status.value,
        "memory_status": result.memory_status.value,
        "disk_status": result.disk_status.value,
        "error": None,
    }


def generate_json(results: list[HealthcheckResult]) -> str:
    """Gera um relatório JSON."""

    data = [
        result_to_dict(result)
        for result in results
    ]

    return json.dumps(
        data,
        indent=2,
        ensure_ascii=False,
    )


def generate_html(
    results: list[HealthcheckResult],
    template_dir: Path,
) -> str:
    """Gera um relatório HTML utilizando Jinja2."""

    data = [
        result_to_dict(result)
        for result in results
    ]

    try:
        environment = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=True,
        )

        template = environment.get_template("report.html")

        return template.render(
            servers=data,
        )

    except Exception as exc:
        raise ReportError(
            f"Erro ao gerar relatório HTML: {exc}"
        ) from exc
