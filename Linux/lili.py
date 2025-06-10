"""FastAPI application exposing a simple endpoint to run shell commands."""

from __future__ import annotations

import asyncio
from datetime import datetime
from pathlib import Path
from typing import Tuple

from fastapi import FastAPI, HTTPException

app = FastAPI()

# Default location for command logs. Using :class:`Path` eases future customisation.
LOG_FILE = Path("/mnt/api_commands_log.txt")


async def run_bash_command(cmd: str) -> Tuple[str, str]:
    """Run a shell command asynchronously and return decoded output."""
    process = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout_bytes, stderr_bytes = await process.communicate()
    return stdout_bytes.decode(), stderr_bytes.decode()


def log_command(command: str, stdout: str, stderr: str) -> None:
    """Append command execution details to ``LOG_FILE``."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with LOG_FILE.open("a", encoding="utf-8") as log_file:
        log_file.write(f"[{timestamp}] Command: {command}\n")
        log_file.write(f"Stdout: {stdout}\n")
        log_file.write(f"Stderr: {stderr}\n\n")


@app.get("/run")
async def run_command(command: str):
    """Execute ``command`` and return its output."""
    if not command:
        raise HTTPException(status_code=400, detail="Command cannot be empty")

    stdout, stderr = await run_bash_command(command)
    log_command(command, stdout, stderr)

    if stderr:
        raise HTTPException(status_code=500, detail=stderr.strip())
    return {"stdout": stdout, "stderr": stderr}
