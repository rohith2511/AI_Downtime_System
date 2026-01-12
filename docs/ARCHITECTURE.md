# Architecture

## Layers
- **Application (FastAPI)**: synthetic failure endpoints (`/load`, `/error`, `/crash`) plus `/metrics` for Prometheus. Background loop samples host metrics (CPU, memory), latency p95, and error rate.
- **Intelligence**: rule + trend logic. Rules check crit/warn thresholds; trend compares 5m vs previous 10m averages. Output is LOW/MEDIUM/HIGH with a reason string and an optional action.
- **Recovery**: guarded shell script (`recovery/self_heal.sh`). Only runs on HIGH when cool-down is satisfied.
- **Observability**: Prometheus scrapes FastAPI `/metrics` and Node Exporter. Grafana consumes Prometheus for dashboards/overlays.

## Data flow
1. Middleware records request latency/error counts (Prometheus counters/histograms + in-memory deques).
2. Background `monitor_loop` (every `windows.sampling_interval_seconds`) builds a snapshot:
   - psutil CPU %, memory %
   - error rate per minute (rolling)
   - latency p95 (rolling, 15m retention by default)
3. `rules.evaluate` scores risk using thresholds and trends. Decision is stored for `/health` and `/state`.
4. On HIGH + action + cool-down passed, `recovery/self_heal.sh` executes. Recovery events logged in memory.
5. Prometheus scrapes `/metrics`; Grafana overlays risk level via PromQL or annotation API.

## Configurability
- Thresholds, windows, cooldowns: `intelligence/config.yaml`
- Recovery action: swap `systemctl` restart target or call orchestrator (ECS/K8s) inside `self_heal.sh`.
- Sampling interval: `windows.sampling_interval_seconds` (15s default)

## Extensibility ideas
- Add file watcher to reload config without restart.
- Push recovery_log to DynamoDB/S3 for audit.
- Emit alerts to Slack/Email via webhook when decision is HIGH.
- Add circuit-breaker to pause recovery after N failures.
