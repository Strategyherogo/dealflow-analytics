#!/bin/bash

# Simple DealFlow Analytics Deployment to DigitalOcean
# This script deploys using DigitalOcean App Platform (easier than Droplet)

set -e

echo "🚀 DealFlow Analytics - Simple DigitalOcean Deployment"
echo "======================================================"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_step() {
    echo -e "${GREEN}[STEP]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check if doctl is installed
if ! command -v doctl &> /dev/null; then
    print_warning "doctl CLI not installed. Installing now..."
    
    # Detect OS and install doctl
    if [[ "$OSTYPE" == "darwin"* ]]; then
        brew install doctl
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        wget https://github.com/digitalocean/doctl/releases/download/v1.94.0/doctl-1.94.0-linux-amd64.tar.gz
        tar xf doctl-1.94.0-linux-amd64.tar.gz
        sudo mv doctl /usr/local/bin
    else
        print_error "Please install doctl manually from: https://github.com/digitalocean/doctl"
        exit 1
    fi
fi

# Check if user is authenticated
print_step "Checking DigitalOcean authentication..."
if ! doctl account get &> /dev/null; then
    print_warning "Not authenticated. Please enter your DigitalOcean API token:"
    doctl auth init
fi

# Load environment variables if .env exists
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
    print_step "Loaded environment variables from .env"
else
    print_warning ".env file not found. Creating from template..."
    cp .env.example .env
    print_error "Please edit .env file with your API keys and run this script again"
    exit 1
fi

# Ask for deployment type
echo ""
echo "Choose deployment type:"
echo "1) DigitalOcean App Platform (Easiest - $12/month)"
echo "2) DigitalOcean Droplet with Docker (More control - $24/month)"
echo "3) Local Docker testing only"
read -p "Enter choice (1-3): " DEPLOY_TYPE

case $DEPLOY_TYPE in
    1)
        print_step "Deploying to DigitalOcean App Platform..."
        
        # Create app spec
        print_step "Creating App Platform specification..."
        doctl apps create --spec app.yaml --wait
        
        # Get app ID
        APP_ID=$(doctl apps list --format ID --no-header | head -1)
        
        # Set environment variables
        print_step "Setting environment variables..."
        doctl apps update $APP_ID --spec app.yaml
        
        # Get app URL
        APP_URL=$(doctl apps get $APP_ID --format LiveURL --no-header)
        
        echo ""
        print_step "✅ Deployment Complete!"
        echo "App URL: $APP_URL"
        echo "Health Check: ${APP_URL}/health"
        echo ""
        echo "Update extension/js/popup.js with:"
        echo "const API_BASE_URL = '${APP_URL}/api';"
        ;;
        
    2)
        print_step "Creating DigitalOcean Droplet..."
        
        # Create droplet
        DROPLET_NAME="dealflow-$(date +%s)"
        doctl compute droplet create $DROPLET_NAME \
            --size s-2vcpu-4gb \
            --image docker-20-04 \
            --region nyc1 \
            --ssh-keys $(doctl compute ssh-key list --format ID --no-header | head -1) \
            --user-data-file cloud-init.yaml \
            --wait
        
        # Get droplet IP
        DROPLET_IP=$(doctl compute droplet list --format PublicIPv4 --no-header | head -1)
        
        print_step "Waiting for droplet to be ready..."
        sleep 60
        
        # Copy files
        print_step "Copying application files..."
        scp -r -o StrictHostKeyChecking=no backend root@$DROPLET_IP:/root/dealflow-analytics/
        scp -o StrictHostKeyChecking=no .env root@$DROPLET_IP:/root/dealflow-analytics/backend/
        
        # Start services
        print_step "Starting services..."
        ssh -o StrictHostKeyChecking=no root@$DROPLET_IP << 'EOF'
cd /root/dealflow-analytics/backend
docker-compose up -d
EOF
        
        echo ""
        print_step "✅ Deployment Complete!"
        echo "Server IP: $DROPLET_IP"
        echo "API URL: http://$DROPLET_IP:8000"
        echo "Health Check: http://$DROPLET_IP:8000/health"
        echo ""
        echo "Update extension/js/popup.js with:"
        echo "const API_BASE_URL = 'http://$DROPLET_IP:8000/api';"
        echo ""
        echo "For HTTPS, point your domain to $DROPLET_IP and run:"
        echo "ssh root@$DROPLET_IP 'cd /root/dealflow-analytics && ./setup-ssl.sh your-domain.com'"
        ;;
        
    3)
        print_step "Starting local Docker environment..."
        
        cd backend
        
        # Build and start containers
        docker-compose down
        docker-compose up -d --build
        
        # Wait for services
        print_step "Waiting for services to start..."
        sleep 10
        
        # Check health
        if curl -f http://localhost:8000/health &> /dev/null; then
            print_step "✅ Local deployment successful!"
            echo ""
            echo "API URL: http://localhost:8000"
            echo "Health Check: http://localhost:8000/health"
            echo "Logs: docker-compose logs -f"
            echo ""
            echo "Extension is already configured for localhost"
        else
            print_error "Services failed to start. Check logs: docker-compose logs"
        fi
        ;;
        
    *)
        print_error "Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "📋 Next Steps:"
echo "1. Test the API endpoint with: curl \$(API_URL)/health"
echo "2. Load the Chrome extension in developer mode"
echo "3. Test analyzing a company on LinkedIn or Crunchbase"
echo ""
echo "🔧 Useful Commands:"
echo "• View logs: doctl apps logs $APP_ID --follow"
echo "• Restart app: doctl apps create-deployment $APP_ID"
echo "• Scale up: doctl apps update $APP_ID --spec app.yaml"
echo ""
print_step "Happy analyzing! 🎯"