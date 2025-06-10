import asyncio
from pathlib import Path

from fastapi.testclient import TestClient

from Linux import lili


def test_run_command_success(tmp_path, monkeypatch):
    log_file = tmp_path / "log.txt"
    monkeypatch.setattr(lili, "LOG_FILE", log_file)
    client = TestClient(lili.app)
    response = client.get("/run", params={"command": "echo hello"})
    assert response.status_code == 200
    assert response.json()["stdout"].strip() == "hello"
    assert log_file.exists()


def test_run_command_error(tmp_path, monkeypatch):
    log_file = tmp_path / "log.txt"
    monkeypatch.setattr(lili, "LOG_FILE", log_file)
    client = TestClient(lili.app)
    response = client.get("/run", params={"command": "bash -c 'echo err >&2; exit 1'"})
    assert response.status_code == 500
    assert "err" in response.json()["detail"]


def test_run_command_empty():
    client = TestClient(lili.app)
    response = client.get("/run", params={"command": ""})
    assert response.status_code == 400
