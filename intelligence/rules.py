from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

from . import trends


@dataclass
class RiskDecision:
    level: str
    reason: str
    triggers: List[str]
    action: Optional[str]


def evaluate(snapshot: Dict, history: List[Dict], config: Dict) -> RiskDecision:
    thresholds = config["thresholds"]
    windows = config["windows"]
    short_window, long_window = trends.slice_windows(history, windows["short_minutes"], windows["long_minutes"])

    triggers: List[str] = []
    level = "LOW"

    cpu_high = snapshot["cpu_percent"] >= thresholds["cpu"]["crit"]
    mem_high = snapshot["memory_percent"] >= thresholds["memory"]["crit"]
    error_high = snapshot["error_rate_per_min"] >= thresholds["error_rate_per_min"]["crit"]
    latency_high = snapshot["latency_p95_ms"] >= thresholds["latency_p95_ms"]["crit"]

    if (cpu_high and mem_high) or error_high or latency_high:
        level = "HIGH"
        if cpu_high and mem_high:
            triggers.append("cpu+memory saturated")
        if error_high:
            triggers.append("error rate critical")
        if latency_high:
            triggers.append("latency p95 critical")

    if level != "HIGH":
        warn_hits: List[str] = []
        if snapshot["cpu_percent"] >= thresholds["cpu"]["warn"]:
            warn_hits.append("cpu warn")
        if snapshot["memory_percent"] >= thresholds["memory"]["warn"]:
            warn_hits.append("memory warn")
        if snapshot["error_rate_per_min"] >= thresholds["error_rate_per_min"]["warn"]:
            warn_hits.append("error rate warn")
        if snapshot["latency_p95_ms"] >= thresholds["latency_p95_ms"]["warn"]:
            warn_hits.append("latency warn")
        if warn_hits:
            level = "MEDIUM"
            triggers.extend(warn_hits)

    cpu_trend = trends.trend_delta(short_window, long_window, "cpu_percent")
    mem_trend = trends.trend_delta(short_window, long_window, "memory_percent")

    if level == "MEDIUM" and cpu_trend["direction"] == "up" and cpu_trend["delta"] >= 5:
        level = "HIGH"
        triggers.append("cpu climbing fast")

    if level == "MEDIUM" and mem_trend["direction"] == "up" and mem_trend["delta"] >= 5:
        level = "HIGH"
        triggers.append("memory climbing fast")

    reason_parts = triggers or ["stable"]
    reason = ", ".join(reason_parts)
    action = config["actions"].get("high_risk") if level == "HIGH" else None

    return RiskDecision(level=level, reason=reason, triggers=triggers, action=action)
