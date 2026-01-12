from __future__ import annotations

from datetime import datetime, timedelta
from statistics import mean
from typing import Dict, List, Tuple


def slice_windows(history: List[Dict], short_minutes: int, long_minutes: int) -> Tuple[List[Dict], List[Dict]]:
    now = datetime.utcnow()
    short_cutoff = now - timedelta(minutes=short_minutes)
    long_cutoff = now - timedelta(minutes=long_minutes)
    short_window = [m for m in history if m["timestamp"] >= short_cutoff]
    long_window = [m for m in history if long_cutoff <= m["timestamp"] < short_cutoff]
    return short_window, long_window


def moving_average(values: List[float]) -> float:
    
    return mean(values) if values else 0.0


def trend_delta(short_window: List[Dict], long_window: List[Dict], key: str) -> Dict:
    short_vals = [m.get(key, 0.0) for m in short_window]
    long_vals = [m.get(key, 0.0) for m in long_window]
    short_avg = moving_average(short_vals)
    long_avg = moving_average(long_vals)
    delta = short_avg - long_avg
    direction = "up" if delta > 0 else "flat" if abs(delta) < 0.1 else "down"
    return {
        "short_avg": short_avg,
        "long_avg": long_avg,
        "delta": delta,
        "direction": direction,
    }


def percentile(data: List[float], percent: float) -> float:
    if not data:
        return 0.0
    data_sorted = sorted(data)
    k = (len(data_sorted) - 1) * (percent / 100.0)
    f = int(k)
    c = min(f + 1, len(data_sorted) - 1)
    if f == c:
        return data_sorted[int(k)]
    d0 = data_sorted[f] * (c - k)
    d1 = data_sorted[c] * (k - f)
    return d0 + d1
