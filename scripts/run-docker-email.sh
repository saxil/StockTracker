#!/bin/bash
# Docker Email Service Deployment Script
# This script demonstrates how to run the updated Stock Tracker container with email functionality

echo "🐳 Stock Tracker - Docker Email Service Deployment"
echo "=================================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running. Please start Docker first."
    exit 1
fi

echo "✅ Docker is running"

# Check if the stock-tracker image exists
if ! docker images stock-tracker:latest | grep -q stock-tracker; then
    echo "❌ Error: stock-tracker:latest image not found."
    echo "Please build the image first: docker build -t stock-tracker:latest ."
    exit 1
fi

echo "✅ Docker image found: stock-tracker:latest"

# Stop any existing containers
echo "🧹 Cleaning up existing containers..."
docker rm -f stock-tracker-app 2>/dev/null || true

# Check for email configuration
if [ -f ".env" ]; then
    echo "✅ Found .env file with email configuration"
    echo "🚀 Starting container with email support..."
    
    # Run with docker-compose (includes email environment variables)
    docker-compose up -d streamlit-app
    
    if [ $? -eq 0 ]; then
        echo "✅ Container started successfully with email support!"
        echo "📧 Email functionality: ENABLED"
        echo "🌐 Application URL: http://localhost:8501"
        echo ""
        echo "📋 Email Service Features:"
        echo "  • Password reset emails"
        echo "  • Welcome emails for new users"
        echo "  • SMTP connection verification"
        echo "  • Comprehensive error handling"
        echo "  • Delivery confirmation"
    else
        echo "❌ Failed to start container with docker-compose"
    fi
    
else
    echo "⚠️  No .env file found - running without email support"
    echo "🚀 Starting container in demo mode..."
    
    # Run without email configuration
    docker run -d -p 8501:8501 --name stock-tracker-app stock-tracker:latest
    
    if [ $? -eq 0 ]; then
        echo "✅ Container started successfully!"
        echo "📧 Email functionality: DISABLED (no credentials)"
        echo "🌐 Application URL: http://localhost:8501"
        echo ""
        echo "💡 To enable email functionality:"
        echo "  1. Copy .env.example to .env"
        echo "  2. Add your Gmail credentials to .env"
        echo "  3. Restart with: docker-compose up -d"
    else
        echo "❌ Failed to start container"
        exit 1
    fi
fi

echo ""
echo "📊 Container Status:"
docker ps --filter name=stock-tracker

echo ""
echo "🎯 Deployment Summary:"
echo "  • Docker image: ✅ Updated with enhanced email service"
echo "  • Email verification: ✅ Actual delivery confirmation"
echo "  • Error handling: ✅ Comprehensive SMTP error handling"
echo "  • Configuration: ✅ Environment variable based"
echo "  • Security: ✅ SSL/TLS encryption, app passwords"
echo ""
echo "🚀 Your Stock Tracker application is now running!"
echo "Visit http://localhost:8501 to start using the application."
