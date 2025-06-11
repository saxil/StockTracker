#!/bin/bash
# Production deployment script

set -e

DOMAIN="yourdomain.com"
EMAIL="your-email@example.com"

echo "🚀 Starting deployment for $DOMAIN..."

# Stop existing containers
docker-compose -f docker-compose.prod.yml down

# Pull latest code
git pull origin main

# Build new image
docker-compose -f docker-compose.prod.yml build --no-cache

# Start containers
docker-compose -f docker-compose.prod.yml up -d

# Wait for services to start
echo "⏳ Waiting for services to start..."
sleep 10

# Setup SSL certificate if it doesn't exist
if [ ! -f /etc/letsencrypt/live/$DOMAIN/fullchain.pem ]; then
    echo "🔒 Setting up SSL certificate..."
    sudo certbot certonly --webroot \
        --webroot-path=/var/www/certbot \
        --email $EMAIL \
        --agree-tos \
        --no-eff-email \
        -d $DOMAIN \
        -d www.$DOMAIN
    
    # Reload nginx
    docker-compose -f docker-compose.prod.yml restart nginx
fi

# Check if everything is running
if docker-compose -f docker-compose.prod.yml ps | grep -q "Up"; then
    echo "✅ Deployment successful!"
    echo "🌐 Your app is now available at: https://$DOMAIN"
else
    echo "❌ Deployment failed. Check logs:"
    docker-compose -f docker-compose.prod.yml logs
    exit 1
fi
