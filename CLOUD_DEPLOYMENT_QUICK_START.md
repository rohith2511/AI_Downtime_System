# Cloud Deployment Quick Reference

## 📱 One-Click Deployment Links

| Platform | Setup | Deploy | Cost |
|----------|-------|--------|------|
| **Render** | [Create Account](https://dashboard.render.com) | `render.yaml` included | $19/mo |
| **Railway** | [Create Account](https://railway.app) | `railway.yaml` included | $5-20/mo |
| **Fly.io** | [Create Account](https://fly.io) | `fly.toml` included | Free tier |
| **Vercel** | [Create Account](https://vercel.com) | `vercel.json` included | Free |
| **Heroku** | [Create Account](https://heroku.com) | Need `Procfile` | $14/mo |

---

## 🚀 Super Quick Start (Choose One)

### RENDER (Full Stack - Easiest)
```bash
# 1. Push to GitHub
git push origin main

# 2. Go to https://dashboard.render.com
# 3. Click "New Web Service"
# 4. Connect GitHub repo
# 5. Deploy button appears!
```

### RAILWAY (Pay-as-you-go - Cheapest)
```bash
# 1. Install CLI
npm i -g @railway/cli

# 2. Login
railway login

# 3. Deploy
cd ai-downtime-system
railway up

# 4. View status
railway status
```

### FLY.IO (Global - Fastest)
```bash
# 1. Install CLI
curl -L https://fly.io/install.sh | sh

# 2. Login
flyctl auth login

# 3. Deploy
cd ai-downtime-system
flyctl deploy

# 4. Open
flyctl open
```

### VERCEL (Dashboard Only - Free)
```bash
# 1. Install CLI
npm i -g vercel

# 2. Deploy
cd dashboard
vercel --prod

# 3. Done! Update API URL in HTML
```

---

## 🔧 Environment Variables (All Platforms)

Copy these to each platform's environment settings:

```env
# Application
PYTHONUNBUFFERED=1
PORT=8000
WORKERS=4
ENVIRONMENT=production

# Database (provided by platform)
DATABASE_URL=postgresql://...
REDIS_URL=redis://...

# Optional
CONFIG_PATH=/etc/ai-downtime/config.yaml
```

---

## 📊 Feature Comparison

```
┌─────────────┬──────────────┬──────────┬────────────┐
│ Platform    │ Backend Only │ Full DB  │ Monitoring │
├─────────────┼──────────────┼──────────┼────────────┤
│ Render      │      ✅      │    ✅    │     ✅     │
│ Railway     │      ✅      │    ✅    │     ✅     │
│ Fly.io      │      ✅      │    ✅    │     ✅     │
│ Vercel*     │      ❌      │    ❌    │     ❌     │
│ Heroku      │      ✅      │    ✅    │     ❌     │
│ AWS AppRun  │      ✅      │    ✅    │     ✅     │
└─────────────┴──────────────┴──────────┴────────────┘
* Vercel is frontend only - pair with backend on another platform
```

---

## 💰 Cost Breakdown

### Budget Option (~$5-10/mo)
- Backend: Railway.app ($5-10/mo)
- Dashboard: Vercel (free)
- **Total: $5-10/mo**

### Standard Production (~$20/mo)
- Backend: Render ($12/mo) + PostgreSQL ($7/mo) + Redis ($7/mo)
- Dashboard: Vercel free
- **Total: ~$26/mo**

### Enterprise (~$100+/mo)
- Backend: AWS App Runner ($20/mo)
- Database: RDS ($50/mo)
- Cache: ElastiCache ($20/mo)
- Monitoring: Datadog ($50/mo)
- **Total: $140+/mo**

---

## ✅ Deployment Checklist

### Before Deploying
- [ ] Code pushed to GitHub main branch
- [ ] Docker image builds locally: `docker build -f docker/Dockerfile .`
- [ ] Health check works: `curl http://localhost:8000/health`
- [ ] Secrets are NOT in code (use platform env vars)

### After Deploying
- [ ] Test health endpoint: `curl https://your-api.onrender.com/health`
- [ ] Check logs for errors
- [ ] Verify database connection
- [ ] Test a synthetic load: `curl https://your-api.onrender.com/load?seconds=5`
- [ ] Check metrics: `curl https://your-api.onrender.com/metrics`

### Security
- [ ] Change default passwords
- [ ] Enable HTTPS (automatic on all platforms)
- [ ] Restrict database access to app only
- [ ] Set up secrets in platform's vault
- [ ] Enable backups on database

---

## 🆘 Troubleshooting

### "Port is already in use" (Local)
```bash
lsof -i :8000
kill -9 <PID>
```

### "Database connection refused" (Cloud)
```bash
# Check connection string format
postgresql://user:password@host:5432/database

# Test connection locally
psql "postgresql://..."
```

### "Image pull failed" (Render/Railway)
```bash
# Make sure docker/Dockerfile exists
# Re-push to trigger rebuild
git push origin main
```

### "Out of memory" (Cloud)
```bash
# Reduce WORKERS count
WORKERS=2

# Or upgrade service tier
# Render: Pro plan ($12+/mo)
# Railway: Bigger allocation
```

### Logs not showing
```bash
# Render
https://dashboard.render.com → Service → Logs

# Railway
railway logs -s api --follow

# Fly.io
flyctl logs --follow

# Vercel
vercel list → Select project → Logs
```

---

## 🔄 Auto-Deployment (GitHub)

All platforms support auto-deployment on push:

1. Connect GitHub repo in platform dashboard
2. Select main branch
3. Enable auto-deploy
4. Push to GitHub:
   ```bash
   git add .
   git commit -m "Deploy to cloud"
   git push origin main
   ```

Platform automatically rebuilds and deploys!

---

## 📈 Scaling After Deployment

### Horizontal Scaling (More Instances)
- **Render:** Upgrade plan
- **Railway:** Increase instances slider
- **Fly.io:** `flyctl scale count=3`
- **Vercel:** Automatic

### Vertical Scaling (More CPU/RAM)
- **Render:** Upgrade to Pro/Pro+ plan
- **Railway:** Increase resource allocation
- **Fly.io:** Edit fly.toml `[build]` cpu/memory
- **Vercel:** Automatic for paid

### Database Scaling
- **Render:** Upgrade PostgreSQL plan
- **Railway:** Increase instance size
- **Fly.io:** Edit fly.toml volumes
- **AWS RDS:** Multi-AZ, read replicas

---

## 🎯 Recommended Path

1. **Try locally first** (Docker Compose)
   ```bash
   docker compose up -d
   ```

2. **Pick a platform:**
   - ✅ **Want easy?** → Render.com
   - ✅ **Want cheap?** → Railway.app
   - ✅ **Want global?** → Fly.io
   - ✅ **Want frontend?** → Vercel

3. **Deploy backend:**
   ```bash
   # Follow platform-specific guide above
   ```

4. **Deploy dashboard:**
   ```bash
   # If using Vercel
   vercel --prod
   
   # Update API URL in dashboard/index.html
   ```

5. **Test endpoints:**
   ```bash
   curl https://your-api.platform.com/health
   curl https://your-dashboard.platform.com
   ```

6. **Monitor:**
   ```bash
   # Check logs on platform dashboard
   # Watch metrics at /metrics
   # View dashboard in browser
   ```

---

## 📚 Full Docs

See [CLOUD_DEPLOYMENT.md](CLOUD_DEPLOYMENT.md) for complete guides including:
- Step-by-step setup for each platform
- Environment variable configuration
- Database creation and backup
- Monitoring and alerting setup
- Scaling and optimization
- Troubleshooting details

---

## 🚀 Next Steps

1. Create account on chosen platform
2. Connect your GitHub repository
3. Configure environment variables
4. Click deploy!

**Questions?** Each platform has excellent docs:
- [Render Docs](https://render.com/docs)
- [Railway Docs](https://docs.railway.app)
- [Fly.io Docs](https://fly.io/docs)
- [Vercel Docs](https://vercel.com/docs)
