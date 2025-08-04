#!/bin/bash

# DealFlow Analytics - DigitalOcean Deployment Script
# This script sets up the complete infrastructure on DigitalOcean

set -e

echo "🚀 DealFlow Analytics - DigitalOcean Deployment"
echo "=============================================="

# Configuration
DROPLET_NAME="dealflow-analytics"
DROPLET_SIZE="s-2vcpu-4gb"  # $24/month
DROPLET_REGION="nyc1"
DROPLET_IMAGE="docker-20-04"
DOMAIN_NAME="your-domain.com"  # Change this to your domain

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_step() {
    echo -e "${GREEN}[STEP]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if doctl is installed
if ! command -v doctl &> /dev/null; then
    print_error "doctl CLI is not installed. Please install it from: https://github.com/digitalocean/doctl"
    exit 1
fi

# Check if docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker Desktop"
    exit 1
fi

print_step "Checking DigitalOcean authentication..."
if ! doctl account get &> /dev/null; then
    print_error "Not authenticated with DigitalOcean. Run: doctl auth init"
    exit 1
fi

# Get environment variables
read -p "Enter your Anthropic API Key: " ANTHROPIC_API_KEY
read -p "Enter database password (will create new): " DB_PASSWORD
read -p "Enter your domain name (e.g., api.dealflow.com): " DOMAIN_NAME

print_step "Creating DigitalOcean Droplet..."
DROPLET_ID=$(doctl compute droplet create $DROPLET_NAME \
    --size $DROPLET_SIZE \
    --image $DROPLET_IMAGE \
    --region $DROPLET_REGION \
    --ssh-keys $(doctl compute ssh-key list --format ID --no-header) \
    --wait \
    --format ID \
    --no-header)

if [ -z "$DROPLET_ID" ]; then
    print_error "Failed to create droplet"
    exit 1
fi

print_step "Droplet created with ID: $DROPLET_ID"

# Get droplet IP
DROPLET_IP=$(doctl compute droplet get $DROPLET_ID --format PublicIPv4 --no-header)
print_step "Droplet IP: $DROPLET_IP"

print_step "Waiting for droplet to be ready..."
sleep 60

print_step "Setting up environment file..."
cat > .env << EOF
ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY
DB_PASSWORD=$DB_PASSWORD
REDIS_HOST=redis
REDIS_PORT=6379
DATABASE_URL=postgresql://dealflow:$DB_PASSWORD@postgres:5432/dealflow
DOMAIN_NAME=$DOMAIN_NAME
EOF

print_step "Copying files to droplet..."
scp -o StrictHostKeyChecking=no -r ../backend root@$DROPLET_IP:/root/dealflow-analytics
scp -o StrictHostKeyChecking=no .env root@$DROPLET_IP:/root/dealflow-analytics/backend/

print_step "Setting up application on droplet..."
ssh -o StrictHostKeyChecking=no root@$DROPLET_IP << 'EOF'
cd /root/dealflow-analytics/backend

# Update system
apt-get update && apt-get upgrade -y

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/download/v2.20.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Install certbot for SSL
apt-get install -y certbot

# Create SSL directory
mkdir -p ssl

# Start the services
docker-compose up -d

echo "✅ Services started successfully!"
EOF

print_step "Setting up SSL certificate..."
ssh -o StrictHostKeyChecking=no root@$DROPLET_IP << EOF
# Stop nginx temporarily for certificate generation
docker-compose stop nginx

# Generate SSL certificate
certbot certonly --standalone -d $DOMAIN_NAME --non-interactive --agree-tos --email admin@$DOMAIN_NAME

# Copy certificates
cp /etc/letsencrypt/live/$DOMAIN_NAME/fullchain.pem /root/dealflow-analytics/backend/ssl/
cp /etc/letsencrypt/live/$DOMAIN_NAME/privkey.pem /root/dealflow-analytics/backend/ssl/

# Update nginx config with correct domain
sed -i "s/your-domain.com/$DOMAIN_NAME/g" /root/dealflow-analytics/backend/nginx.conf

# Restart services
cd /root/dealflow-analytics/backend
docker-compose up -d

echo "🔒 SSL certificate installed successfully!"
EOF

print_step "Setting up firewall..."
ssh -o StrictHostKeyChecking=no root@$DROPLET_IP << 'EOF'
# Configure UFW
ufw --force enable
ufw allow ssh
ufw allow 80
ufw allow 443
ufw reload

echo "🔥 Firewall configured successfully!"
EOF

print_step "Setting up monitoring and auto-renewal..."
ssh -o StrictHostKeyChecking=no root@$DROPLET_IP << EOF
# Add cron job for SSL renewal
echo "0 12 * * * /usr/bin/certbot renew --quiet && docker-compose restart nginx" | crontab -

# Add log rotation
echo "/root/dealflow-analytics/backend/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    notifempty
    create 0644 root root
}" > /etc/logrotate.d/dealflow

echo "📊 Monitoring and maintenance configured!"
EOF

print_step "Creating backup script..."
ssh -o StrictHostKeyChecking=no root@$DROPLET_IP << 'EOF'
cat > /root/backup.sh << 'BACKUP_EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/root/backups"
mkdir -p $BACKUP_DIR

# Backup database
docker exec dealflow-postgres pg_dump -U dealflow dealflow > $BACKUP_DIR/db_backup_$DATE.sql

# Backup Redis
docker exec dealflow-redis redis-cli BGSAVE
docker cp dealflow-redis:/data/dump.rdb $BACKUP_DIR/redis_backup_$DATE.rdb

# Keep only last 7 days of backups
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "*.rdb" -mtime +7 -delete

echo "Backup completed: $DATE"
BACKUP_EOF

chmod +x /root/backup.sh

# Schedule daily backups
echo "0 2 * * * /root/backup.sh" | crontab -

echo "💾 Backup system configured!"
EOF

print_step "Testing deployment..."
sleep 30

# Test API endpoint
if curl -f "https://$DOMAIN_NAME/health" &> /dev/null; then
    print_step "✅ API is responding correctly!"
else
    print_warning "API test failed. Check logs with: ssh root@$DROPLET_IP 'cd /root/dealflow-analytics/backend && docker-compose logs'"
fi

echo ""
echo "🎉 Deployment Complete!"
echo "======================"
echo "• Server IP: $DROPLET_IP"
echo "• API URL: https://$DOMAIN_NAME"
echo "• Health Check: https://$DOMAIN_NAME/health"
echo "• API Docs: https://$DOMAIN_NAME/docs"
echo ""
echo "📋 Next Steps:"
echo "1. Update your Chrome extension to use: https://$DOMAIN_NAME"
echo "2. Point your domain $DOMAIN_NAME to IP: $DROPLET_IP"
echo "3. Test the extension with the new API endpoint"
echo ""
echo "🔧 Management Commands:"
echo "• View logs: ssh root@$DROPLET_IP 'cd /root/dealflow-analytics/backend && docker-compose logs -f'"
echo "• Restart services: ssh root@$DROPLET_IP 'cd /root/dealflow-analytics/backend && docker-compose restart'"
echo "• Update application: ssh root@$DROPLET_IP 'cd /root/dealflow-analytics/backend && git pull && docker-compose up -d --build'"
echo ""
echo "💰 Monthly Cost: ~$24 (Droplet) + ~$5 (Additional services) = $29/month"
echo ""
print_step "Deployment script completed successfully!"