from fastapi import FastAPI, HTTPException
import subprocess
from datetime import datetime

app = FastAPI()

LOG_FILE = "/mnt/api_commands_log.txt"

def run_bash_command(cmd):
    process = subprocess.Popen(["/bin/bash", "-c", cmd], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    return stdout, stderr

def log_command(command, stdout, stderr):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as log_file:
        log_file.write(f"[{timestamp}] Command: {command}\n")
        log_file.write(f"Stdout: {stdout}\n")
        log_file.write(f"Stderr: {stderr}\n")
        log_file.write("\n")

@app.get("/run")
def run_command(command: str):
    if not command:
        raise HTTPException(status_code=400, detail="Command cannot be empty")
    stdout, stderr = run_bash_command(command)
    log_command(command, stdout.decode(), stderr.decode())
    return {"stdout": stdout.decode(), "stderr": stderr.decode()}
