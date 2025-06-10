"""FastAPI app exposing endpoints for Windows command execution."""

from __future__ import annotations

from asyncio.subprocess import PIPE, create_subprocess_exec
from fastapi import FastAPI, HTTPException

# Initialize the FastAPI app
app = FastAPI()

# Function to retrieve secure data without authentication
@app.get("/secure-data/")
def secure_data():
    return {"message": "Secure Data Accessed"}

# Function to execute a PowerShell command securely without authentication
@app.post("/run/")
async def run_powershell_command(cmd: str):
    if "dangerous_keyword" in cmd.lower():
        raise HTTPException(status_code=400, detail="Unsafe command blocked")

    process = await create_subprocess_exec(
        "powershell",
        "-Command",
        cmd,
        stdout=PIPE,
        stderr=PIPE,
    )
    stdout_bytes, stderr_bytes = await process.communicate()
    stdout, stderr = stdout_bytes.decode(), stderr_bytes.decode()

    if process.returncode != 0:
        raise HTTPException(status_code=500, detail=f"PowerShell error: {stderr.strip()}")

    return {"message": stdout}

# Function to read an item without authentication
@app.get("/items/{item_id}")
async def read_item(item_id: int):
    return {"item_id": item_id}
