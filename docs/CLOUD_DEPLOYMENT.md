# Cloud Deployment Guide

Deploy your AI Downtime Guard system to popular cloud platforms.

## 📋 Supported Platforms

| Platform | Type | Best For | Cost | Setup Time |
|----------|------|----------|------|-----------|
| **Render.com** | Full-stack | Backend + DB + Cache | $7-50/mo | 15 min |
| **Vercel** | Frontend | Dashboard UI | Free-$20/mo | 5 min |
| **Railway.app** | Full-stack | Backend + DB + Cache | Pay-as-you-go | 10 min |
| **Fly.io** | Docker | Full stack in 6 regions | Free tier available | 20 min |
| **Heroku** | Full-stack | Backend + DB | $7-50/mo | 15 min |
| **AWS App Runner** | Docker | Managed serverless | $0.06/hour | 20 min |

---

## 🚀 OPTION 1: Render.com (Recommended for Full Stack)

**Best for:** Complete production deployment with DB and caching

### Prerequisites
- Render.com account (free tier available)
- GitHub repository connected

### Steps

1. **Connect Your Repository**
   ```bash
   # Push code to GitHub
   git push origin main
   ```

2. **Create Render Service**
   - Go to https://dashboard.render.com
   - Click "New +" → "Web Service"
   - Connect your GitHub repo
   - Select this repo from the list

3. **Configure Service**
   - **Name:** ai-downtime-api
   - **Runtime:** Docker
   - **Region:** Oregon (or your preference)
   - **Plan:** Pro ($12/month) - includes health checks
   - **Dockerfile:** docker/Dockerfile

4. **Add Environment Variables**
   ```
   PYTHONUNBUFFERED = 1
   WORKERS = 4
   ENVIRONMENT = production
   ```

5. **Create PostgreSQL Database**
   - In Render Dashboard: "New +" → "PostgreSQL"
   - **Name:** ai-downtime-db
   - **Database:** ai_downtime
   - **User:** ai_downtime
   - Plan: Starter ($7/month)
   - Copy the connection string

6. **Create Redis Cache**
   - In Render Dashboard: "New +" → "Redis"
   - **Name:** ai-downtime-redis
   - Plan: Starter
   - Copy the connection URL

7. **Link Services**
   ```bash
   # Add to Web Service environment variables:
   DATABASE_URL = postgresql://ai_downtime:password@db-url/ai_downtime
   REDIS_URL = redis://:password@redis-url:6379
   ```

8. **Deploy Dashboard (Static)**
   - Create another service: "New +" → "Static Site"
   - **Name:** ai-downtime-dashboard
   - **Build Command:** (leave empty - static HTML)
   - **Publish Directory:** dashboard
   - **Root Directory:** /

9. **Set Up Auto-Deployment**
   - Enable "Auto-deploy" on main branch
   - Configure GitHub push trigger

### Verify Deployment
```bash
curl https://your-api.onrender.com/health
curl https://your-dashboard.onrender.com
```

**Cost Estimate:** ~$19/month (API + DB + Redis)

---

## 🎨 OPTION 2: Vercel (For Dashboard Only)

**Best for:** Hosting the beautiful Tailwind dashboard UI

### Prerequisites
- Vercel account (free)
- GitHub connected

### Steps

1. **Deploy Dashboard**
   ```bash
   npm install -g vercel
   cd dashboard
   vercel
   ```

2. **Interactive Setup**
   ```
   ? Which scope? [Select your personal account]
   ? Link to existing project? No
   ? What's your project's name? ai-downtime-dashboard
   ? In which directory is your code? ./
   ? Want to modify vercel.json? Yes
   ```

3. **Configure vercel.json**
   Already provided in root directory

4. **Add API Endpoint**
   - Update `dashboard/index.html` with your backend URL:
   ```javascript
   const API_BASE = 'https://your-api.onrender.com';
   ```

5. **Deploy**
   ```bash
   vercel --prod
   ```

6. **GitHub Auto-Deployment**
   - Connect GitHub repo in Vercel dashboard
   - Auto-deploys on push to main

**Cost:** Free tier sufficient, paid if needed: $20/month

**Live URL:** `https://your-dashboard.vercel.app`

---

## 🚂 OPTION 3: Railway.app (Alternative Full Stack)

**Best for:** Fast, simple full-stack deployment with pay-as-you-go pricing

### Prerequisites
- Railway.app account
- GitHub connected

### Steps

1. **Install Railway CLI**
   ```bash
   npm i -g @railway/cli
   railway login
   ```

2. **Initialize Project**
   ```bash
   cd ai-downtime-system
   railway init
   ```

3. **Configure railway.yaml**
   Already provided in root directory

4. **Connect Services**
   ```bash
   railway add
   # Select: PostgreSQL
   railway add
   # Select: Redis
   ```

5. **Deploy**
   ```bash
   railway up
   ```

6. **View Status**
   ```bash
   railway status
   ```

7. **Get Connection URLs**
   ```bash
   railway variables
   ```

8. **GitHub Integration**
   - Go to Railway Dashboard → Project Settings
   - Enable GitHub auto-deploy
   - Select main branch

**Cost:** ~$5-10/month (pay only for what you use)

**Access:**
```bash
railway open -s api      # Opens API logs
railway logs -s postgres # Database logs
```

---

## 🪰 OPTION 4: Fly.io (Global Distribution)

**Best for:** Global audience, auto-scaling, multiple regions

### Prerequisites
- Fly.io account (free tier available)
- flyctl CLI installed

### Steps

1. **Install Fly CLI**
   ```bash
   curl -L https://fly.io/install.sh | sh
   flyctl auth login
   ```

2. **Generate Configuration**
   ```bash
   cd ai-downtime-system
   flyctl launch
   ```
   
   This creates `fly.toml` (already provided)

3. **Configure Environment**
   ```bash
   flyctl secrets set DATABASE_URL="postgresql://..."
   flyctl secrets set REDIS_URL="redis://..."
   ```

4. **Deploy**
   ```bash
   flyctl deploy
   ```

5. **Monitor**
   ```bash
   flyctl status
   flyctl logs
   flyctl ssh console  # SSH into container
   ```

6. **Scale to Multiple Regions**
   ```bash
   flyctl regions add jnb  # Johannesburg
   flyctl regions add syd  # Sydney
   flyctl regions add lon  # London
   ```

**Cost:** Free tier + $5.70/month base + usage ($0.0000011/CPU-second)

**Access:**
```bash
flyctl open        # Opens in browser
flyctl dash        # Dashboard
```

---

## 🏗️ OPTION 5: Heroku (Classic Option)

**Best for:** Simple deployment, traditional approach

### Prerequisites
- Heroku account
- Heroku CLI installed

### Steps

1. **Create Procfile**
   ```bash
   cat > Procfile << 'EOF'
   web: gunicorn -k uvicorn.workers.UvicornWorker -w 4 -b 0.0.0.0:$PORT app.main:app
   EOF
   ```

2. **Create app**
   ```bash
   heroku create ai-downtime-api
   heroku stack:set container  # Use Docker
   ```

3. **Add PostgreSQL**
   ```bash
   heroku addons:create heroku-postgresql:hobby-dev
   ```

4. **Add Redis**
   ```bash
   heroku addons:create heroku-redis:premium-0
   ```

5. **Deploy**
   ```bash
   git push heroku main
   heroku logs --tail
   ```

**Cost:** ~$14/month (Postgres hobby + Redis premium)

---

## 🔧 OPTION 6: AWS App Runner (Serverless Docker)

**Best for:** Managed container deployment without Kubernetes complexity

### Prerequisites
- AWS account
- AWS CLI configured
- Docker image in ECR

### Steps

1. **Push Docker Image to ECR**
   ```bash
   aws ecr create-repository --repository-name ai-downtime-app
   aws ecr get-login-password | docker login --username AWS --password-stdin YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com
   docker build -t ai-downtime-app:latest docker/
   docker tag ai-downtime-app:latest YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/ai-downtime-app:latest
   docker push YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/ai-downtime-app:latest
   ```

2. **Create App Runner Service**
   ```bash
   aws apprunner create-service \
     --service-name ai-downtime-api \
     --source-configuration \
       ImageRepository={ImageIdentifier=YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/ai-downtime-app:latest,ImageRepositoryType=ECR,ImageConfiguration={Port=8000}} \
     --cpu 0.5 \
     --memory 1024 \
     --region us-east-1
   ```

3. **Set Environment Variables**
   ```bash
   aws apprunner update-service \
     --service-arn arn:aws:apprunner:us-east-1:ACCOUNT_ID:service/ai-downtime-api/SERVICE_ID \
     --auto-scaling-configuration-arn arn:aws:apprunner:us-east-1:ACCOUNT_ID:autoscalingconfiguration/default \
     --network-configuration EgressConfiguration={EgressType=VPC,VpcConnectorArn=arn:aws:apprunner:us-east-1:ACCOUNT_ID:vpcconnector/default}
   ```

4. **Create RDS PostgreSQL**
   ```bash
   aws rds create-db-instance \
     --db-instance-identifier ai-downtime-db \
     --db-instance-class db.t3.micro \
     --engine postgres \
     --master-username ai_downtime \
     --master-user-password YOUR_SECURE_PASSWORD \
     --allocated-storage 20
   ```

5. **Create ElastiCache Redis**
   ```bash
   aws elasticache create-cache-cluster \
     --cache-cluster-id ai-downtime-redis \
     --cache-node-type cache.t3.micro \
     --engine redis \
     --num-cache-nodes 1
   ```

**Cost:** ~$20-30/month (App Runner + RDS + ElastiCache)

---

## 📊 Comparison Matrix

```
┌─────────────┬─────────────┬──────────────┬─────────────┬──────────┐
│ Platform    │ Full Stack  │ Cost/Month   │ Setup Time  │ Features │
├─────────────┼─────────────┼──────────────┼─────────────┼──────────┤
│ Render.com  │     ✅      │   $19-50     │    15 min   │ Solid    │
│ Railway.app │     ✅      │   $5-20      │    10 min   │ Modern   │
│ Fly.io      │     ✅      │   $5-15      │    20 min   │ Global   │
│ Heroku      │     ✅      │   $14-50     │    15 min   │ Classic  │
│ AWS AppRun  │     ✅      │   $20-40     │    30 min   │ Powerful │
│ Vercel      │     ❌*     │   Free-20    │     5 min   │ Fast     │
└─────────────┴─────────────┴──────────────┴─────────────┴──────────┘
* Vercel can host frontend + connect to separate API backend
```

---

## 🔐 Security Checklist Before Production

- [ ] Change all default passwords in environment variables
- [ ] Enable HTTPS on all services (automatic on most platforms)
- [ ] Set up SSL certificates
- [ ] Configure firewall rules (restrict DB to app only)
- [ ] Enable backups for PostgreSQL
- [ ] Set up monitoring and alerting
- [ ] Configure secrets management
- [ ] Enable audit logging
- [ ] Test database recovery procedures

---

## 📱 Monitoring After Deployment

### Health Checks
```bash
# Render
curl https://your-api.onrender.com/health

# Railway
railway logs -s api

# Fly.io
flyctl logs

# Vercel
vercel list
```

### View Metrics
```bash
# Prometheus (if exposed)
https://your-api.onrender.com/metrics

# Application logs
https://dashboard.render.com  # Render logs
https://railway.app/dashboard # Railway logs
https://fly.io/dashboard      # Fly.io dashboard
```

---

## 🚨 Troubleshooting

### Service won't start
```bash
# Check logs
render:  https://dashboard.render.com (Logs tab)
railway: railway logs -s api
fly.io:  flyctl logs
heroku:  heroku logs --tail
```

### Database connection fails
```bash
# Verify connection string format
postgresql://user:password@host:5432/database

# Test locally first
psql "postgresql://..."
```

### Memory/CPU issues
- Upgrade service tier
- Reduce WORKERS count
- Enable caching layer (Redis)

### High latency
- Switch to region closer to users
- Enable Redis caching
- Use CDN for static assets (Vercel)

---

## 📚 Next Steps

1. **Choose platform** based on needs/budget
2. **Create accounts** on selected platforms
3. **Connect GitHub** repository
4. **Configure environment variables** with secure secrets
5. **Deploy** using provided configs
6. **Test** health endpoints
7. **Monitor** logs and metrics
8. **Set up CI/CD** for automatic deployments

---

## 💡 Recommended Setup

**For Small Teams (Low Cost):**
- Backend: Railway.app ($5-10/mo)
- Dashboard: Vercel (Free)
- Total: ~$5-10/month

**For Production:**
- Backend: Render.com or Fly.io ($15-20/mo)
- Dashboard: Vercel ($20/mo) or Render Static
- Monitoring: Datadog/New Relic ($50-100/mo)
- Total: ~$50-100/month

**For Enterprise:**
- Backend: AWS EKS/App Runner ($100-500/mo)
- Dashboard: CloudFront + S3 ($50-200/mo)
- Monitoring: Datadog Enterprise ($500+/mo)
- Database: RDS Multi-AZ ($200-1000/mo)
- Total: $1000+/month

---

**Questions?** Check platform docs:
- [Render Docs](https://render.com/docs)
- [Railway Docs](https://docs.railway.app)
- [Fly.io Docs](https://fly.io/docs)
- [Vercel Docs](https://vercel.com/docs)
