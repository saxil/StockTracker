# StockTracker API Documentation

## Overview

The StockTracker application provides stock monitoring and email notification services.

## Project Structure

```
src/stock_tracker/
├── __init__.py              # Package initialization
├── main.py                  # Main application entry point
├── config/
│   ├── __init__.py
│   ├── auth.py             # Authentication utilities
│   └── settings.py         # Application settings
├── models/
│   ├── __init__.py
│   └── stock.py            # Stock data models
├── services/
│   ├── __init__.py
│   └── email_service.py    # Email notification service
├── utils/
│   ├── __init__.py
│   ├── email_diagnostics.py
│   ├── email_test.py
│   ├── try_email.py
│   └── try_email_improved.py
└── templates/
    └── email/              # Email templates
```

## Configuration

Create a `.env` file in the project root with the following variables:

```env
# Email Configuration
EMAIL_ADDRESS=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587

# Stock API Keys
ALPHA_VANTAGE_API_KEY=your-alpha-vantage-key
FINNHUB_API_KEY=your-finnhub-key

# Application Settings
DEBUG=False
LOG_LEVEL=INFO
USERS_FILE=data/users.json
```

## Installation

```bash
# Install in development mode
pip install -e .

# Install with development dependencies
pip install -e ".[dev]"
```

## Usage

```bash
# Run the main application
python -m stock_tracker.main

# Or use the console script
stock-tracker
```

## Docker

The application includes Docker configuration for containerized deployment.

```bash
# Build and run with Docker Compose
docker-compose up --build

# Production deployment
docker-compose -f docker-compose.prod.yml up --build
```
