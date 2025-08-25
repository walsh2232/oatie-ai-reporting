#!/usr/bin/env python3
"""Cross-platform watchdog for Oatie services.

Features:
* Monitors backend health endpoint and frontend root.
* Restarts processes when consecutive failures exceed threshold.
* Minimal dependencies (stdlib only).
* Can optionally (re)create venv & install deps on cold start.
"""
from __future__ import annotations

import os
import subprocess
import sys
import time
import urllib.request
from dataclasses import dataclass

BACKEND_PORT = int(os.getenv("OATIE_BACKEND_PORT", "8000"))
FRONTEND_PORT = int(os.getenv("OATIE_FRONTEND_PORT", "5173"))
INTERVAL = float(os.getenv("OATIE_WATCH_INTERVAL", "15"))
THRESHOLD = int(os.getenv("OATIE_WATCH_THRESHOLD", "3"))
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BACKEND_DIR = os.path.join(PROJECT_ROOT, "backend")
FRONTEND_DIR = os.path.join(PROJECT_ROOT, "frontend")
PYTHON = sys.executable

backend_proc: subprocess.Popen | None = None
frontend_proc: subprocess.Popen | None = None


def log(msg: str, level: str = "INFO"):
    ts = time.strftime("%Y-%m-%dT%H:%M:%S")
    print(f"[{ts}][{level}] {msg}", flush=True)


def http_ok(url: str, timeout: float = 5) -> bool:
    try:
        with urllib.request.urlopen(url, timeout=timeout) as r:  # nosec: B310
            return 200 <= r.status < 500
    except Exception:
        return False


def start_backend():
    global backend_proc
    if backend_proc and backend_proc.poll() is None:
        log("Backend already running", "DEBUG")
        return
    log("Starting backend...")
    cmd = [PYTHON, "-m", "app.main"]
    backend_proc = subprocess.Popen(cmd, cwd=BACKEND_DIR)


def start_frontend():
    global frontend_proc
    if frontend_proc and frontend_proc.poll() is None:
        log("Frontend already running", "DEBUG")
        return
    log("Starting frontend (npm run dev)...")
    npm_cmd = ["npm", "run", "dev"]
    frontend_proc = subprocess.Popen(npm_cmd, cwd=FRONTEND_DIR, shell=(os.name == "nt"))


def stop(proc: subprocess.Popen | None, name: str):
    if proc and proc.poll() is None:
        log(f"Stopping {name}", "WARN")
        proc.terminate()
        try:
            proc.wait(5)
        except subprocess.TimeoutExpired:
            proc.kill()


def main():
    backend_bad = 0
    frontend_bad = 0

    start_backend()
    start_frontend()

    while True:
        time.sleep(INTERVAL)
        if http_ok(f"http://localhost:{BACKEND_PORT}/health/live"):
            backend_bad = 0
        else:
            backend_bad += 1
        if http_ok(f"http://localhost:{FRONTEND_PORT}/"):
            frontend_bad = 0
        else:
            frontend_bad += 1

        if backend_bad >= THRESHOLD:
            log(f"Backend unhealthy {backend_bad} times - restarting", "WARN")
            stop(backend_proc, "backend")
            start_backend()
            backend_bad = 0
        if frontend_bad >= THRESHOLD:
            log(f"Frontend unhealthy {frontend_bad} times - restarting", "WARN")
            stop(frontend_proc, "frontend")
            start_frontend()
            frontend_bad = 0


if __name__ == "__main__":  # pragma: no cover
    try:
        main()
    except KeyboardInterrupt:
        log("Watchdog exiting", "INFO")
        stop(backend_proc, "backend")
        stop(frontend_proc, "frontend")
