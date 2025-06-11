#!/bin/bash
# Server setup script for Ubuntu/Debian

# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install Nginx
sudo apt install nginx -y

# Install Certbot for SSL
sudo apt install certbot python3-certbot-nginx -y

# Clone your repository
git clone https://github.com/saxil/StockTracker.git
cd StockTracker

# Create environment file
echo "GMAIL_EMAIL=your-email@gmail.com" > .env
echo "GMAIL_APP_PASSWORD=your-app-password" >> .env

# Build and run with Docker Compose
docker-compose up -d

echo "Setup complete! Configure your domain DNS to point to this server's IP address."
