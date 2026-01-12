from __future__ import annotations

import asyncio
import logging
import os
import shutil
import subprocess
import time
from collections import deque
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Deque, Dict, Tuple

import psutil
import yaml
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, PlainTextResponse, Response
from fastapi.staticfiles import StaticFiles
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

from intelligence import rules, trends

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s - %(message)s")
logger = logging.getLogger("ai-downtime")

BASE_DIR = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG_PATH = BASE_DIR / "intelligence" / "config.yaml"
RECOVERY_SCRIPT = BASE_DIR / "recovery" / "self_heal.sh"

app = FastAPI(title="AI Downtime Guard", version="0.1.0")

REQUEST_LATENCY = Histogram("app_request_latency_seconds", "Request latency", ["endpoint"])
REQUEST_COUNT = Counter("app_request_total", "Total requests", ["endpoint", "status"])
ERROR_COUNT = Counter("app_error_total", "Total error responses", ["endpoint"])

latency_samples: Deque[Tuple[datetime, float]] = deque(maxlen=5000)
error_events: Deque[datetime] = deque(maxlen=2000)
metrics_history: Deque[Dict[str, Any]] = deque(maxlen=500)
state: Dict[str, Any] = {
    "last_decision": None,
    "recovery_log": [],
}
config: Dict[str, Any] = {}
last_recovery_at: datetime | None = None
last_alert_at: datetime | None = None

# Serve dashboard static files if present
dashboard_dir = BASE_DIR / "dashboard"
if dashboard_dir.exists():
    app.mount("/dashboard", StaticFiles(directory=dashboard_dir, html=True), name="dashboard")


def load_config() -> Dict[str, Any]:
    env_path = os.getenv("CONFIG_PATH")
    cfg_path = Path(env_path).expanduser() if env_path else DEFAULT_CONFIG_PATH
    if not cfg_path.exists():
        raise FileNotFoundError(f"Config not found at {cfg_path}")
    with open(cfg_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def prune_latency(now: datetime, window_seconds: int) -> None:
    cutoff = now - timedelta(seconds=window_seconds)
    while latency_samples and latency_samples[0][0] < cutoff:
        latency_samples.popleft()


def compute_error_rate(now: datetime, window_seconds: int = 60) -> float:
    cutoff = now - timedelta(seconds=window_seconds)
    while error_events and error_events[0] < cutoff:
        error_events.popleft()
    return (len(error_events) * 60.0) / float(window_seconds)


def build_snapshot(now: datetime) -> Dict[str, Any]:
    cpu_percent = psutil.cpu_percent(interval=None)
    mem_percent = psutil.virtual_memory().percent
    error_rate_per_min = compute_error_rate(now)
    prune_latency(now, window_seconds=config["windows"]["long_minutes"] * 60)
    latencies_ms = [lat * 1000 for _, lat in latency_samples]
    latency_p95_ms = trends.percentile(latencies_ms, 95)

    snapshot = {
        "timestamp": now,
        "cpu_percent": cpu_percent,
        "memory_percent": mem_percent,
        "error_rate_per_min": error_rate_per_min,
        "latency_p95_ms": latency_p95_ms,
    }
    return snapshot


def should_recover(now: datetime) -> bool:
    global last_recovery_at
    cooldown = config["cooldowns"]["recovery_seconds"]
    if last_recovery_at is None:
        return True
    return (now - last_recovery_at).total_seconds() >= cooldown


def trigger_recovery(reason: str) -> None:
    global last_recovery_at
    if os.name == "nt":
        logger.warning("Skipping recovery on Windows host (no native bash)")
        return
    if not RECOVERY_SCRIPT.exists():
        logger.warning("Recovery script missing: %s", RECOVERY_SCRIPT)
        return
    bash_path = shutil.which("bash")
    if bash_path is None:
        logger.warning("Skipping recovery: bash not available on this host")
        return
    try:
        subprocess.run([bash_path, str(RECOVERY_SCRIPT)], check=True)
        last_recovery_at = datetime.utcnow()
        state["recovery_log"].append({
            "timestamp": last_recovery_at.isoformat(),
            "reason": reason,
        })
        logger.warning("Recovery executed due to: %s", reason)
    except subprocess.CalledProcessError as exc:
        logger.error("Recovery failed: %s", exc)


async def monitor_loop() -> None:
    global state
    sampling_interval = config["windows"]["sampling_interval_seconds"]
    while True:
        now = datetime.utcnow()
        snapshot = build_snapshot(now)
        metrics_history.append(snapshot)
        decision = rules.evaluate(snapshot, list(metrics_history), config)
        state["last_decision"] = {
            "level": decision.level,
            "reason": decision.reason,
            "timestamp": now.isoformat(),
        }
        if decision.level == "HIGH" and decision.action and should_recover(now):
            trigger_recovery(decision.reason)
        await asyncio.sleep(sampling_interval)


@app.on_event("startup")
async def startup_event() -> None:
    global config
    global metrics_history
    config = load_config()
    metrics_history = deque(maxlen=config["windows"].get("history_points", 500))
    psutil.cpu_percent(interval=None)
    asyncio.create_task(monitor_loop())


@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start = time.perf_counter()
    status_code = 500
    try:
        response = await call_next(request)
        status_code = response.status_code
    except Exception:
        status_code = 500
        raise
    finally:
        duration = time.perf_counter() - start
        endpoint = request.url.path
        REQUEST_LATENCY.labels(endpoint=endpoint).observe(duration)
        REQUEST_COUNT.labels(endpoint=endpoint, status=str(status_code)).inc()
        latency_samples.append((datetime.utcnow(), duration))
        if status_code >= 500:
            ERROR_COUNT.labels(endpoint=endpoint).inc()
            error_events.append(datetime.utcnow())
    return response


@app.get("/health")
def health() -> Dict[str, Any]:
    decision = state.get("last_decision") or {}
    return {
        "status": "ok",
        "risk_level": decision.get("level", "LOW"),
        "reason": decision.get("reason", "booting"),
        "timestamp": decision.get("timestamp", datetime.utcnow().isoformat()),
    }


@app.get("/load")
def create_load(seconds: int = 5) -> Dict[str, Any]:
    seconds = max(1, min(seconds, 30))
    end = time.time() + seconds
    while time.time() < end:
        _ = sum(i * i for i in range(10000))
    return {"message": "synthetic CPU load generated", "seconds": seconds}


@app.get("/error")
def throw_error() -> Dict[str, Any]:
    raise HTTPException(status_code=500, detail="Simulated failure")


@app.get("/crash")
def crash() -> None:
    os._exit(1)


@app.get("/metrics")
def metrics() -> Response:
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/state")
def state_snapshot() -> Dict[str, Any]:
    latest = state.get("last_decision") or {}
    return {
        "decision": latest,
        "recent_recoveries": state.get("recovery_log", []),
    }


@app.get("/")
def root() -> Dict[str, str]:
    return {"message": "AI Downtime Guard running", "docs": "/docs"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=False)
