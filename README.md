# Enhanced Stock Tracker

A comprehensive stock tracking and analysis application built with Streamlit featuring advanced technical analysis, portfolio management, price alerts, and AI-powered predictions.

## 🚀 Quick Start (No Setup Required!)

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/StockTracker.git
cd StockTracker

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the application
streamlit run app.py

# 4. Open your browser to http://localhost:8501
```

**That's it!** No API keys, no configuration files, no database setup required. Just install and run!

### Alternative: Use the startup scripts
```bash
# Windows
start.bat

# Linux/Mac
./start.sh
```

Visit the live application: [Enhanced Stock Tracker](https://your-app-name.streamlit.app)

## 📋 Features

### 📊 Stock Analysis
- **Real-time Stock Data**: Fetch current and historical stock prices using Yahoo Finance
- **Interactive Charts**: Beautiful, interactive candlestick charts powered by Plotly
- **15+ Technical Indicators**: SMA, EMA, RSI, MACD, Bollinger Bands, Stochastic, ATR, CCI, Williams %R, VWAP, OBV, and more
- **Trading Signals**: Automated buy/sell/neutral signals based on technical analysis
- **Support & Resistance**: Automatic identification of key price levels
- **Fibonacci Retracement**: Calculate and display Fibonacci levels

### 💼 Portfolio Management
- **Holdings Tracking**: Add and manage stock holdings with purchase dates and prices
- **Performance Analytics**: Real-time portfolio value, gains/losses, and percentage returns
- **Allocation Analysis**: Visual portfolio allocation with pie charts and performance graphs
- **Dividend Tracking**: Monitor dividend income and yields
- **Export Functionality**: Download portfolio data as CSV files
- **Rebalancing Suggestions**: AI-powered portfolio rebalancing recommendations

### 🔔 Smart Alerts System
- **Price Alerts**: Set alerts for price above/below thresholds
- **Percentage Change Alerts**: Get notified on significant price movements
- **Email Notifications**: Receive alert notifications via email
- **Alert History**: Track triggered alerts and statistics
- **Multiple Alert Types**: Support for various alert conditions

### 🎯 AI-Powered Predictions
- **Machine Learning Models**: Random Forest and Linear Regression for price forecasting
- **Customizable Timeframes**: Predict prices 1-90 days into the future
- **Model Accuracy Metrics**: MAE, RMSE, and performance indicators
- **Visual Predictions**: Interactive charts showing predicted vs historical prices
- **Prediction Export**: Download predictions as CSV data

### 🔐 User Management
- **Secure Authentication**: Login system with user profiles
- **Favorites System**: Save and quickly access favorite stocks
- **Analysis History**: Track all your stock analyses
- **Password Reset**: Email-based password recovery
- **User Preferences**: Personalized settings and configurations

### 💾 Data Persistence
- **SQLite Database**: Robust data storage for stocks, portfolios, alerts, and analysis history
- **Historical Data Storage**: Automatic storage of fetched stock data
- **Analysis Caching**: Save and retrieve analysis results
- **Portfolio History**: Track portfolio performance over time

## 🛠️ Technologies Used

- **Streamlit** - Web application framework
- **Yahoo Finance API** - Stock data source
- **Plotly** - Interactive visualizations
- **scikit-learn** - Machine learning models
- **SQLite** - Database for data persistence
- **Pandas** - Data manipulation and analysis
- **NumPy** - Numerical computing
- **Python 3.8+** - Core programming language

## 🏗️ Project Structure

```
StockTracker/
├── src/
│   └── stock_tracker/
│       ├── __init__.py
│       ├── main.py                 # Original Streamlit app
│       ├── config/
│       │   ├── __init__.py
│       │   ├── auth.py             # Authentication system
│       │   └── settings.py         # Application settings
│       ├── models/
│       │   ├── __init__.py
│       │   ├── stock.py            # Stock data models
│       │   └── database.py         # Database management
│       ├── services/
│       │   ├── __init__.py
│       │   └── email_service.py    # Email notifications
│       ├── utils/
│       │   ├── __init__.py
│       │   ├── technical_analysis.py    # Technical indicators
│       │   ├── portfolio.py             # Portfolio management
│       │   └── alert_system.py          # Price alerts system
│       └── templates/
│           └── email/              # Email templates
├── tests/
│   ├── __init__.py
│   ├── test_database.py           # Database tests
│   ├── test_technical_analysis.py # Technical analysis tests
│   ├── test_portfolio.py          # Portfolio tests
│   ├── test_email_service.py      # Email service tests
│   └── fixtures/                  # Test data fixtures
├── data/
│   ├── stocks.db                  # SQLite database
│   └── users.json                 # User data
├── docs/                          # Documentation
├── app.py                         # Enhanced Streamlit application
├── app.py                         # Original application
├── auth.py                        # Authentication module
├── run_tests.py                   # Test runner
├── requirements.txt               # Dependencies
└── README.md                      # This file
```

## 🏃‍♂️ Running Locally

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Setup Instructions

1. **Clone the repository:**
```bash
git clone https://github.com/yourusername/StockTracker.git
cd StockTracker
```

2. **Create a virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Run the enhanced application:**
```bash
streamlit run app.py
```

6. **Open your browser to:** `http://localhost:5000`

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Verify everything works (no API keys required)
python verify_setup.py

# Run all tests
python run_tests.py

# Run tests with coverage report
python run_tests.py --coverage

# Run specific test modules
python -m pytest tests/test_database.py -v
python -m pytest tests/test_technical_analysis.py -v
python -m pytest tests/test_portfolio.py -v
```

## 🛠️ Troubleshooting

### Common Issues

**❓ "Module not found" errors**
```bash
# Make sure you're in the correct directory and dependencies are installed
pip install -r requirements.txt
```

**❓ "No data available" for stocks**
```bash
# Test if Yahoo Finance is accessible
python verify_setup.py
```

**❓ Email alerts not working**
- This is normal! Email is completely optional
- See `docs/EMAIL_SETUP.md` if you want email notifications
- All other features work without email setup

**❓ Database errors**
- The app automatically creates its SQLite database
- Delete `data/stocks.db` if you want to reset everything

## 🔧 Configuration

### Email Configuration (Optional)
For alert notifications, set up email configuration:

1. **Create environment variables:**
```bash
# Windows
set EMAIL_ADDRESS=your-email@gmail.com
set EMAIL_PASSWORD=your-app-password

# Linux/Mac
export EMAIL_ADDRESS=your-email@gmail.com
export EMAIL_PASSWORD=your-app-password
```

2. **Or create `.streamlit/secrets.toml`:**
```toml
[email]
EMAIL_ADDRESS = "your-email@gmail.com"
EMAIL_PASSWORD = "your-app-password"
```

### Database Configuration
The application automatically creates a SQLite database in the `data/` directory. No additional configuration required.

### Stock Data Source
This application uses **Yahoo Finance (yfinance)** which provides free stock data without requiring any API keys or subscriptions. Simply install the requirements and start using the app!

## 📊 Usage Guide

### Getting Started
1. **Create an account** or login with existing credentials
2. **Analyze stocks** by entering symbols (e.g., AAPL, GOOGL, MSFT)
3. **Add to portfolio** to track your investments
4. **Set up alerts** for price movements
5. **Explore technical analysis** with advanced indicators
6. **Generate predictions** using AI models

### Key Features

#### Stock Analysis
- Enter any stock symbol (e.g., AAPL, GOOGL, TSLA)
- Choose analysis timeframe (1mo to 5y)
- View real-time data, charts, and key metrics
- Get automated trading signals

#### Portfolio Management
- Add holdings with purchase price and date
- Monitor real-time performance
- View allocation and returns
- Export data for external analysis

#### Price Alerts
- Set price threshold alerts
- Configure percentage change notifications
- Receive email notifications (if configured)
- Track alert history and statistics

#### Technical Analysis
- 15+ technical indicators
- Support and resistance levels
- Fibonacci retracement levels
- Advanced charting with multiple timeframes

#### AI Predictions
- Machine learning price forecasting
- Multiple model options (Random Forest, Linear Regression)
- Customizable prediction timeframes
- Model accuracy metrics

## 📦 Deployment

This app is deployed on Streamlit Community Cloud. To deploy your own version:

1. Fork this repository
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub account
4. Select your forked repository
5. Set the main file path to `app.py` (or `base_app.py` for basic version)
6. Deploy!

**No API keys required!** The app uses Yahoo Finance which provides free data.

## 🔧 Configuration

The app uses environment variables for sensitive data. Create a `.streamlit/secrets.toml` file for local development (optional):

```toml
[email]
GMAIL_EMAIL = "your-email@gmail.com"
GMAIL_APP_PASSWORD = "your-app-password"
```

Email configuration is only needed if you want to receive alert notifications.

## 📊 Popular Stock Symbols

Try these popular symbols in the app:
- **AAPL** - Apple Inc.
- **GOOGL** - Alphabet Inc.
- **MSFT** - Microsoft Corporation
- **TSLA** - Tesla Inc.
- **AMZN** - Amazon.com Inc.
- **NVDA** - NVIDIA Corporation

## ❓ Frequently Asked Questions

**Q: Do I need any API keys?**  
A: No! The app uses Yahoo Finance which provides free data without requiring API keys.

**Q: Do I need to set up email?**  
A: No, email is completely optional. It's only needed if you want to receive price alert notifications.

**Q: What databases do I need to install?**  
A: None! The app uses SQLite which is built into Python. The database file is created automatically.

**Q: Can I use this for real trading?**  
A: This is for educational and analysis purposes only. Always consult with financial professionals before making investment decisions.

**Q: Does this work offline?**  
A: You need an internet connection to fetch current stock data, but the analysis and portfolio features work with cached data.

**Q: Is my data safe?**  
A: All data is stored locally on your computer in a SQLite database. Nothing is sent to external servers except for fetching stock prices from Yahoo Finance.

## ⚠️ Disclaimer

This tool is for informational purposes only and should not be considered as financial advice. Always do your own research before making investment decisions.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
