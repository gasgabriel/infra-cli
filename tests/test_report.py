from pathlib import Path

from infra_cli.health_rules import HealthStatus
from infra_cli.healthcheck import HealthcheckResult
from infra_cli.metrics import ServerMetrics
from infra_cli.report import (
    ReportError,
    generate_html,
    generate_json,
    result_to_dict,
)

import pytest


def create_ok_result():
    return HealthcheckResult(
        host="server01",
        metrics=ServerMetrics(
            cpu=25.0,
            memory=40.0,
            disk=50.0,
        ),
        cpu_status=HealthStatus.OK,
        memory_status=HealthStatus.OK,
        disk_status=HealthStatus.OK,
        status=HealthStatus.OK,
        error=None,
    )


def test_result_to_dict():
    result = create_ok_result()

    data = result_to_dict(result)

    assert data["host"] == "server01"
    assert data["cpu"] == 25.0
    assert data["memory"] == 40.0
    assert data["disk"] == 50.0
    assert data["status"] == "OK"
    assert data["cpu_status"] == "OK"
    assert data["memory_status"] == "OK"
    assert data["disk_status"] == "OK"
    assert data["error"] is None


def test_result_to_dict_connection_error():
    result = HealthcheckResult(
        host="server03",
        status=HealthStatus.CONNECTION_ERROR,
        error="Timeout ao conectar",
    )

    data = result_to_dict(result)

    assert data["host"] == "server03"
    assert data["cpu"] is None
    assert data["memory"] is None
    assert data["disk"] is None
    assert data["status"] == "CONNECTION_ERROR"
    assert data["error"] == "Timeout ao conectar"


def test_generate_json():
    result = create_ok_result()

    content = generate_json([result])

    assert '"host": "server01"' in content
    assert '"cpu": 25.0' in content
    assert '"memory": 40.0' in content
    assert '"disk": 50.0' in content
    assert '"status": "OK"' in content


def test_generate_html():
    result = create_ok_result()

    template_dir = Path("templates")

    content = generate_html(
        [result],
        template_dir,
    )

    assert "<html" in content.lower()
    assert "server01" in content
    assert "25.0" in content
    assert "40.0" in content
    assert "50.0" in content

def test_generate_html_invalid_template(tmp_path):
    results = []

    with pytest.raises(
        ReportError,
        match="Erro ao gerar relatório HTML",
    ):
        generate_html(
            results,
            tmp_path,
        )
