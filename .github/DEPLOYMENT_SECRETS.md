# GitHub Actions Secrets Setup

For CI/CD automation to deploy to cloud platforms, add these secrets to your GitHub repository.

## 📋 Where to Add Secrets

1. Go to GitHub repository → Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Add each secret below

---

## 🔑 Required Secrets by Platform

### For Render.com
```
RENDER_API_KEY        = Your Render API key from https://dashboard.render.com/account/api-tokens
RENDER_SERVICE_ID     = Your service ID (shown in Render dashboard URL)
RENDER_DEPLOY_HOOK    = Webhook URL for automatic deployments
```

**Get these:**
1. Log in to Render Dashboard
2. Account → API Tokens → Create new token
3. Copy the token as `RENDER_API_KEY`
4. In Services, click your service, copy the service ID from URL

---

### For Railway.app
```
RAILWAY_TOKEN         = Your Railway API token
RAILWAY_SERVICE       = Your service name (ai-downtime-api)
```

**Get these:**
1. Log in to Railway Dashboard
2. Account → API Tokens → Generate new
3. Copy token as `RAILWAY_TOKEN`
4. Find service name in dashboard

---

### For Fly.io
```
FLY_API_TOKEN         = Your Fly.io API token
FLY_APP_NAME          = Your app name (ai-downtime-system)
```

**Get these:**
1. Log in to Fly Dashboard
2. Account → Access Tokens → Create new
3. Copy token as `FLY_API_TOKEN`
4. App name from fly.toml or dashboard

---

### For Vercel (Dashboard)
```
VERCEL_TOKEN          = Your Vercel API token
VERCEL_ORG_ID         = Your organization ID
VERCEL_PROJECT_ID     = Project ID for dashboard
```

**Get these:**
1. Log in to Vercel Dashboard
2. Account Settings → Tokens → Create new token
3. Copy as `VERCEL_TOKEN`
4. Get IDs from project settings

---

### For AWS (App Runner / EKS)
```
AWS_ACCESS_KEY_ID     = Your AWS access key
AWS_SECRET_ACCESS_KEY = Your AWS secret key
AWS_REGION            = us-east-1 (or your region)
ECR_REGISTRY          = Your ECR registry URL
ECR_REPOSITORY        = ai-downtime-app
```

**Get these:**
1. AWS Console → IAM → Users → Create user
2. Generate access keys
3. Store safely in GitHub secrets
4. ECR info: AWS Console → ECR → Repositories

---

### For Slack Notifications (Optional)
```
SLACK_WEBHOOK_URL     = Your Slack incoming webhook
SLACK_CHANNEL         = #deployments
```

**Get this:**
1. Slack App → Incoming Webhooks → Create new
2. Copy webhook URL

---

## 🚀 GitHub Actions Workflow Setup

### 1. Create `.github/workflows/deploy-cloud.yml`

Already provided! It includes jobs for all platforms:

```yaml
name: Deploy to Cloud Platforms

on:
  push:
    branches: [ main ]
  workflow_dispatch:

jobs:
  deploy-render:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to Render
        run: |
          curl -X POST https://api.render.com/deploy/srv-${{ secrets.RENDER_SERVICE_ID }}?key=${{ secrets.RENDER_API_KEY }}

  deploy-railway:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to Railway
        uses: railway-app/action@v1
        with:
          token: ${{ secrets.RAILWAY_TOKEN }}

  deploy-flyio:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to Fly.io
        uses: superfly/flyctl-actions@master
        with:
          args: "deploy --remote-only"
        env:
          FLY_API_TOKEN: ${{ secrets.FLY_API_TOKEN }}

  deploy-vercel:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy Dashboard to Vercel
        uses: vercel/action@master
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
```

### 2. Add Secrets to GitHub

Visit: **Repository → Settings → Secrets and variables → Actions**

Click "New repository secret" and add:

```
RENDER_API_KEY         = [from Render]
RENDER_SERVICE_ID      = [from Render]
RAILWAY_TOKEN          = [from Railway]
RAILWAY_SERVICE        = ai-downtime-api
FLY_API_TOKEN          = [from Fly.io]
FLY_APP_NAME           = ai-downtime-system
VERCEL_TOKEN           = [from Vercel]
VERCEL_ORG_ID          = [from Vercel]
VERCEL_PROJECT_ID      = [from Vercel]
SLACK_WEBHOOK_URL      = [from Slack] (optional)
```

### 3. Test Workflow

```bash
# Push to main to trigger
git push origin main

# Or manually trigger
# GitHub → Actions → Deploy to Cloud → Run workflow
```

Monitor deployments:
- **GitHub:** Repository → Actions tab
- **Render:** Dashboard → Deploys tab
- **Railway:** Dashboard → Deployments tab
- **Fly.io:** flyctl status
- **Vercel:** Dashboard → Deployments tab

---

## 🔒 Security Best Practices

1. **Never commit secrets** to code
2. **Use short-lived tokens** when available
3. **Rotate tokens regularly** (monthly)
4. **Limit token permissions** to only needed scopes
5. **Enable branch protection** on main branch
6. **Review deployment logs** for errors
7. **Monitor API usage** on each platform

### Secrets Rotation Checklist
- [ ] Monthly: Rotate AWS keys
- [ ] Monthly: Rotate Render API key
- [ ] Monthly: Rotate Railway token
- [ ] Monthly: Rotate Fly.io token
- [ ] Quarterly: Rotate Vercel token
- [ ] On team changes: Revoke old secrets

---

## 📝 Creating API Tokens (Step-by-Step)

### Render.com
1. Log in → Account → API Tokens
2. Click "Create new token"
3. Give it a name: `GitHub Actions`
4. Copy token
5. In GitHub: Settings → Secrets → New secret
6. Name: `RENDER_API_KEY`
7. Value: [paste token]
8. Click Add secret

### Railway.app
1. Log in → Account (avatar) → API Tokens
2. Click "Generate token"
3. Name: `GitHub Actions`
4. Copy token
5. In GitHub: Add as `RAILWAY_TOKEN`

### Fly.io
1. Log in → Account → Access Tokens
2. Click "Create token"
3. Name: `GitHub Actions`
4. Copy token
5. In GitHub: Add as `FLY_API_TOKEN`

### Vercel
1. Log in → Settings → Tokens
2. Click "Create"
3. Name: `GitHub Actions`
4. Scope: Full Account
5. Copy token
6. In GitHub: Add as `VERCEL_TOKEN`
7. Also add `VERCEL_ORG_ID` and `VERCEL_PROJECT_ID` from project settings

### AWS
1. AWS Console → IAM → Users
2. Click "Create user" or select existing
3. Permissions → Create access keys
4. Copy Access Key ID and Secret Access Key
5. In GitHub:
   - Add `AWS_ACCESS_KEY_ID`
   - Add `AWS_SECRET_ACCESS_KEY`
6. **⚠️ CRITICAL:** Use an IAM user with minimal permissions, not root account

---

## 🧪 Test Deployments

### Test Render Deployment
```bash
curl -X POST https://api.render.com/deploy/srv-YOUR_SERVICE_ID?key=YOUR_API_KEY
# Should return 200 with deployment info
```

### Test Railway Deployment
```bash
railway status
railway logs -s api
```

### Test Fly.io Deployment
```bash
flyctl deploy
flyctl status
```

### Test Vercel Deployment
```bash
vercel --prod
# Opens deployment in browser
```

---

## 🚨 Troubleshooting

### "Invalid token" error
- Verify token is correct (check for extra spaces)
- Verify token hasn't expired
- Regenerate new token on platform

### "Permission denied" error
- Token scope too limited
- Create token with full permissions
- For AWS: IAM user needs sufficient permissions

### Workflow not running
- Check if main branch is protected
- Verify workflow file syntax (`.github/workflows/deploy-cloud.yml`)
- Manual trigger: Actions → Deploy to Cloud → Run workflow

### Deployment stuck
- Check platform logs
- Verify database connection
- Check environment variables
- Review application logs

---

## 📊 Recommended Setup

### Minimal (Render only)
```
RENDER_API_KEY
RENDER_SERVICE_ID
```

### Standard (Render + Vercel)
```
RENDER_API_KEY
RENDER_SERVICE_ID
VERCEL_TOKEN
VERCEL_ORG_ID
VERCEL_PROJECT_ID
```

### Complete (All platforms)
```
RENDER_API_KEY
RENDER_SERVICE_ID
RAILWAY_TOKEN
RAILWAY_SERVICE
FLY_API_TOKEN
FLY_APP_NAME
VERCEL_TOKEN
VERCEL_ORG_ID
VERCEL_PROJECT_ID
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
SLACK_WEBHOOK_URL (optional)
```

---

## ✅ Verification Checklist

- [ ] Created secrets in GitHub
- [ ] Verified each secret is spelled correctly
- [ ] Tested each platform's API token works
- [ ] Committed `.github/workflows/deploy-cloud.yml`
- [ ] Pushed to main branch
- [ ] Checked Actions tab for successful runs
- [ ] Verified deployments on each platform

---

## 🔗 Quick Links

- [GitHub Secrets Documentation](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [Render API Documentation](https://render.com/docs/api)
- [Railway Documentation](https://docs.railway.app)
- [Fly.io Documentation](https://fly.io/docs)
- [Vercel Documentation](https://vercel.com/docs)

---

## 💡 Pro Tips

1. **Use environments**: Create dev/staging/prod environments with different secrets
2. **Auto-deploy on tags**: Modify workflow to deploy on releases
3. **Slack notifications**: Add webhook step to notify on deployment
4. **Rollback automation**: Create workflow for rollbacks
5. **Monitor health**: Add post-deployment health checks

Example health check in workflow:
```yaml
- name: Verify Deployment
  run: |
    sleep 30
    curl -f https://your-api.onrender.com/health || exit 1
```

---

**All set!** Your CI/CD pipeline is ready to automatically deploy to multiple cloud platforms.

Push to main and watch it deploy! 🚀
