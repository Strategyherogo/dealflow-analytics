# 🚀 DigitalOcean Deployment Guide for DealFlow Analytics

## Overview
This guide provides three deployment options for DealFlow Analytics on DigitalOcean, from simplest to most customizable.

## Prerequisites
- DigitalOcean account ([Sign up here](https://www.digitalocean.com/) - get $200 credit)
- GitHub account (for App Platform deployment)
- Domain name (optional but recommended for production)

## Option 1: DigitalOcean App Platform (Easiest)
**Cost:** ~$12-20/month  
**Time:** 10 minutes  
**Best for:** Quick deployment, automatic scaling, zero maintenance

### Steps:
1. **Fork the repository to your GitHub**
   ```bash
   # Fork this repo on GitHub, then clone your fork
   git clone https://github.com/YOUR_USERNAME/dealflow-analytics.git
   cd dealflow-analytics
   ```

2. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Connect to DigitalOcean**
   - Go to [DigitalOcean App Platform](https://cloud.digitalocean.com/apps)
   - Click "Create App"
   - Choose "GitHub" as source
   - Select your forked repository
   - Choose branch: `main`

4. **Configure the app**
   - App name: `dealflow-analytics`
   - Region: Choose closest to your users
   - Review the detected Dockerfile
   - Click "Next"

5. **Set environment variables**
   Add these in the App Platform UI:
   - `ANTHROPIC_API_KEY` (encrypted)
   - `GITHUB_TOKEN` (encrypted)
   - `NEWS_API_KEY` (encrypted)
   - `REDIS_HOST` (set to `localhost` for now)

6. **Choose plan**
   - Select "Basic" plan
   - Choose instance size: $12/month (1GB RAM)
   - Click "Launch App"

7. **Update Chrome extension**
   Once deployed, get your app URL and update:
   ```javascript
   // extension/js/popup.js
   const API_BASE_URL = 'https://your-app-name.ondigitalocean.app/api';
   ```

## Option 2: DigitalOcean Droplet with Docker (More Control)
**Cost:** ~$24/month  
**Time:** 20 minutes  
**Best for:** Full control, custom configuration, better performance

### Automated Deployment:
```bash
# Run the simplified deployment script
chmod +x deploy-simple.sh
./deploy-simple.sh

# Choose option 2 when prompted
# Follow the interactive prompts
```

### Manual Deployment:
1. **Create a Droplet**
   ```bash
   doctl compute droplet create dealflow-analytics \
     --size s-2vcpu-4gb \
     --image docker-20-04 \
     --region nyc1 \
     --ssh-keys $(doctl compute ssh-key list --format ID --no-header)
   ```

2. **SSH into the droplet**
   ```bash
   ssh root@YOUR_DROPLET_IP
   ```

3. **Clone and setup**
   ```bash
   git clone https://github.com/YOUR_USERNAME/dealflow-analytics.git
   cd dealflow-analytics/backend
   
   # Copy your .env file
   nano .env  # Paste your environment variables
   
   # Start services
   docker-compose up -d
   ```

4. **Setup SSL (optional but recommended)**
   ```bash
   # Point your domain to the droplet IP first
   ./setup-ssl.sh your-domain.com
   ```

## Option 3: Local Development with Docker
**Cost:** Free  
**Time:** 5 minutes  
**Best for:** Testing, development

```bash
# Quick start
cd dealflow-analytics
chmod +x deploy-simple.sh
./deploy-simple.sh

# Choose option 3 for local deployment
```

Or manually:
```bash
cd backend
docker-compose up -d

# Check if it's working
curl http://localhost:8000/health
```

## Post-Deployment Configuration

### 1. Add a Custom Domain
For App Platform:
- Go to Settings → Domains
- Add your domain
- Update DNS records as instructed

For Droplet:
- Point A record to droplet IP
- Run: `./setup-ssl.sh your-domain.com`

### 2. Configure the Chrome Extension
1. Update API URL in `extension/js/popup.js`
2. Reload extension in Chrome
3. Test on a LinkedIn company page

### 3. Set Up Monitoring
App Platform includes monitoring by default.

For Droplet:
```bash
# Access Netdata monitoring
http://YOUR_DROPLET_IP:19999
```

## Environment Variables Reference

### Required:
- `ANTHROPIC_API_KEY` - For AI analysis (get from [Anthropic Console](https://console.anthropic.com/))

### Optional but Recommended:
- `GITHUB_TOKEN` - Increases GitHub API rate limits
- `NEWS_API_KEY` - For news analysis
- `DB_PASSWORD` - Database password (auto-generated if not set)
- `DOMAIN_NAME` - Your domain for SSL setup

## Troubleshooting

### App Platform Issues:
```bash
# View logs
doctl apps logs YOUR_APP_ID --follow

# Restart app
doctl apps create-deployment YOUR_APP_ID

# Check app status
doctl apps get YOUR_APP_ID
```

### Droplet Issues:
```bash
# SSH into droplet
ssh root@YOUR_DROPLET_IP

# Check logs
docker-compose logs -f

# Restart services
docker-compose restart

# Check container status
docker ps
```

### Extension Not Working:
1. Check console: Right-click extension → Inspect
2. Verify API URL is correct
3. Check CORS settings allow your extension ID

## Cost Optimization

### Minimize costs:
1. **App Platform Basic**: $5/month (512MB RAM) - works for light usage
2. **Droplet**: $12/month (1GB RAM) - minimum viable
3. **Database**: Use SQLite instead of PostgreSQL initially
4. **Redis**: Skip for caching (use in-memory)

### Scale as you grow:
- Start with Basic plan
- Monitor usage in DigitalOcean dashboard
- Scale up when you hit limits

## Security Best Practices

1. **Always use HTTPS in production**
2. **Rotate API keys regularly**
3. **Enable firewall on droplets**:
   ```bash
   ufw allow 22,80,443/tcp
   ufw --force enable
   ```
4. **Set up backups**:
   - App Platform: Automatic
   - Droplet: Enable weekly backups in DO console

## Monitoring & Maintenance

### Health Checks:
- App Platform: `https://your-app.ondigitalocean.app/health`
- Droplet: `http://YOUR_IP:8000/health`

### Updates:
```bash
# App Platform (automatic with GitHub)
git push origin main

# Droplet
ssh root@YOUR_IP
cd /root/dealflow-analytics
git pull
docker-compose up -d --build
```

## Support & Resources

- [DigitalOcean App Platform Docs](https://docs.digitalocean.com/products/app-platform/)
- [DigitalOcean Droplets Guide](https://docs.digitalocean.com/products/droplets/)
- [Docker Compose Reference](https://docs.docker.com/compose/)
- [Our GitHub Issues](https://github.com/YOUR_USERNAME/dealflow-analytics/issues)

## Quick Commands Reference

```bash
# Check deployment status
doctl apps list
doctl compute droplet list

# View logs
doctl apps logs YOUR_APP_ID --follow
ssh root@DROPLET_IP 'docker-compose logs -f'

# Restart services
doctl apps create-deployment YOUR_APP_ID
ssh root@DROPLET_IP 'docker-compose restart'

# Scale up
doctl apps update YOUR_APP_ID --spec app.yaml
doctl compute droplet resize DROPLET_ID --size s-4vcpu-8gb

# Monitor costs
doctl billing-history list
```

## Estimated Monthly Costs

| Component | App Platform | Droplet | Notes |
|-----------|-------------|---------|-------|
| Compute | $12 | $24 | Basic vs 2vCPU/4GB |
| Database | $7 | Included | PostgreSQL |
| Storage | Included | Included | 25GB |
| Bandwidth | Included | Included | 1TB |
| SSL | Free | Free | Let's Encrypt |
| **Total** | **$19/mo** | **$24/mo** | |

## Next Steps

1. ✅ Deploy using one of the methods above
2. ✅ Test the API endpoint
3. ✅ Configure Chrome extension
4. ✅ Test on real company pages
5. 📈 Monitor usage and scale as needed

---

**Need help?** Open an issue or reach out to support@dealflow.com