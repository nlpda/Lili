from fastapi.testclient import TestClient
from types import SimpleNamespace

from Windows import lili


class FakeProcess:
    def __init__(self, stdout=b"", stderr=b"", returncode=0):
        self._stdout = stdout
        self._stderr = stderr
        self.returncode = returncode

    async def communicate(self):
        return self._stdout, self._stderr


async def fake_exec_success(*args, **kwargs):
    return FakeProcess(stdout=b"ok")


async def fake_exec_failure(*args, **kwargs):
    return FakeProcess(stdout=b"", stderr=b"boom", returncode=1)


def test_run_powershell_command_success(monkeypatch):
    monkeypatch.setattr(lili, "create_subprocess_exec", fake_exec_success)
    client = TestClient(lili.app)
    response = client.post("/run/", params={"cmd": "Get-Process"})
    assert response.status_code == 200
    assert response.json()["message"] == "ok"


def test_run_powershell_command_failure(monkeypatch):
    monkeypatch.setattr(lili, "create_subprocess_exec", fake_exec_failure)
    client = TestClient(lili.app)
    response = client.post("/run/", params={"cmd": "Get-Process"})
    assert response.status_code == 500
    assert "boom" in response.json()["detail"]


def test_run_powershell_command_blocked():
    client = TestClient(lili.app)
    response = client.post("/run/", params={"cmd": "dangerous_keyword"})
    assert response.status_code == 400


def test_secure_data():
    client = TestClient(lili.app)
    resp = client.get("/secure-data/")
    assert resp.status_code == 200
    assert resp.json()["message"] == "Secure Data Accessed"
