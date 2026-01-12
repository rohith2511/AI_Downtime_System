# AI Downtime Guard (FastAPI)

Industry-style reliability demo that creates failure modes on purpose, watches them with Prometheus/Grafana, scores risk with lightweight rules + trends, and self-heals with guarded recovery scripts.

## Quickstart (local)
1. Python 3.11+. Create venv and install deps:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. Run FastAPI:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```
3. Exercise failure endpoints:
   - `GET /health` — quick health + risk summary
   - `GET /load?seconds=10` — synthetic CPU load
   - `GET /error` — 500 error spike
   - `GET /crash` — force process exit
4. Metrics exposed at `/metrics` for Prometheus.
5. Web dashboard at `http://localhost:8000/dashboard` for a live UI.

## Dockerized stack
From `docker/` launch FastAPI + Prometheus + Grafana + Node Exporter:
```bash
cd docker
docker compose up -d --build
```
Grafana: http://localhost:3000 (admin/admin). Add Prometheus datasource at `http://prometheus:9090` and import dashboards.

### Production compose
- Persistent volumes for Prometheus (`prometheus_data`) and Grafana (`grafana_data`) are defined; data survives container restarts.
- Restart policies are set to `unless-stopped`; basic CPU/memory limits and reservations are included.
- FastAPI runs via gunicorn/uvicorn workers (defaults: PORT 8000, WORKERS 4). Override with env vars.
- Healthcheck probes `/health` internally to gate restarts.
- To mount a custom config file for rules/thresholds, either uncomment the `CONFIG_PATH` env var and volume in `docker-compose.yml`, or supply an override file such as:
   ```yaml
   # docker-compose.override.yml
   services:
      fastapi-app:
         environment:
            - CONFIG_PATH=/etc/ai-downtime/config.yaml
         volumes:
            - /path/config.yaml:/etc/ai-downtime/config.yaml:ro
   ```
   Then run `docker compose -f docker-compose.yml -f docker-compose.override.yml up -d`.

### Production container run
- Build: `docker build -t ai-downtime:latest -f docker/Dockerfile .`
- Run: `docker run -d -p 8000:8000 --name ai-downtime ai-downtime:latest`
- Override config path if mounting a custom file: `docker run -d -p 8000:8000 -v /path/config.yaml:/etc/config.yaml:ro -e CONFIG_PATH=/etc/config.yaml ai-downtime:latest`

## Cloud Deployment (Render, Vercel, Railway, Fly.io)
See [CLOUD_DEPLOYMENT.md](CLOUD_DEPLOYMENT.md) for step-by-step guides:
- **Render.com** — Full-stack ($19/mo): API + PostgreSQL + Redis
- **Railway.app** — Modern alternative ($5-20/mo)
- **Fly.io** — Global distribution with auto-scaling
- **Vercel** — Frontend dashboard (free-$20/mo)
- **Heroku** — Classic option ($14-50/mo)
- **AWS App Runner** — Serverless containers ($20-40/mo)

Pre-configured files: `render.yaml`, `railway.yaml`, `fly.toml`, `vercel.json`

## Kubernetes Deployment
Deploy to any Kubernetes cluster:
```bash
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/monitoring.yaml
kubectl apply -f k8s/security-rbac.yaml
```
Includes HPA (2-10 pods), network policies, RBAC, PodDisruptionBudget.

## Infrastructure as Code (AWS)
Deploy complete AWS infrastructure with Terraform:
```bash
cd terraform && terraform plan && terraform apply
```
Creates: EKS cluster, RDS PostgreSQL, ElastiCache Redis, VPC, IAM, security groups.

## GitHub Actions CI/CD
Automated deployments on push:
- `.github/workflows/deploy.yml` — Test, build, deploy to dev/prod
- `.github/workflows/deploy-cloud.yml` — Deploy to Render, Railway, Fly.io, Vercel

## Files of interest
- `app/main.py` — FastAPI app, metrics, background risk loop
- `intelligence/rules.py` — rule-based risk scoring + actions
- `intelligence/trends.py` — moving averages and trends
- `intelligence/config.yaml` — thresholds, windows, cooldowns
- `recovery/self_heal.sh` — guarded restart hook
- `monitoring/prometheus.yml` — scrape config for app + node exporter
- `docker/docker-compose.yml` — one-command local stack

## Running on EC2 (t2.micro)
- Install Docker or Python + systemd service for the app.
- Run Node Exporter on the host: `./node_exporter --web.listen-address=:9100`.
- Keep security groups open for 22 (SSH), 3000 (Grafana), 9090 (Prometheus), 8000 (app) as needed.

## Operating notes
- Recovery uses `bash recovery/self_heal.sh`; wire this to `systemctl restart fastapi-app` on the instance.
- Cool-downs prevent restart storms (`cooldowns.recovery_seconds`).
- Trend logic compares last 5 min vs previous 10 min; adjust in `config.yaml`.
- The system is intentionally noisy; use `/load` and `/error` to validate alerting and recovery.
