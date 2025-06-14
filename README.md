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
streamlit run enhanced_app.py

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
- **15+ Technical Indicators**: SMA, EMA, RSI, MACD, Bollinger Bands, Stochastic, ATR, CCI, Williams %R, VWAP, OBV, and more. Prediction models also leverage a rich set of these indicators.
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
- **Email Notifications**: Receive email notifications for triggered alerts (requires SMTP configuration as per `docs/EMAIL_SETUP.md`).
- **Alert History**: Track triggered alerts and statistics
- **Multiple Alert Types**: Support for various alert conditions

### 🎯 AI-Powered Predictions
- **Machine Learning Models**: Utilizes Random Forest, Linear Regression, and Gradient Boosting Regressor for price forecasting.
- **Enhanced Feature Engineering**: Models are trained using a comprehensive set of features, including various technical indicators, for improved accuracy.
- **Customizable Timeframes**: Predict prices 1-90 days into the future.
- **Model Accuracy Metrics**: MAE, RMSE, and performance indicators are displayed.
- **Visual Predictions**: Interactive charts showing predicted vs historical prices.
- **Prediction Export**: Download predictions as CSV data.

### 🔐 User Management
- **Secure Authentication**: Login system with user profiles
- **Favorites System**: Save and quickly access favorite stocks
- **Analysis History**: Track all your stock analyses
- **Password Reset**: Email-based password recovery (may use a separate email configuration, see `auth.py`).
- **User Preferences**: Personalized settings and configurations

### 💾 Data Persistence
- **SQLite Database**: Robust data storage for stocks, portfolios, alerts, and analysis history
- **Historical Data Storage**: Automatic storage of fetched stock data
- **Analysis Caching**: Save and retrieve analysis results
- **Portfolio History**: Track portfolio performance over time

## 🛠️ Technologies Used

- **Streamlit** - Web application framework
- **Yahoo Finance API (yfinance)** - Stock data source
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
│       ├── main.py                 # Original Streamlit app (references PredictionService)
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
│       │   ├── email_service.py    # Handles email notifications for alerts
│       │   └── prediction_service.py    # Core logic for training and generating model-based price predictions
│       ├── utils/
│       │   ├── __init__.py
│       │   ├── technical_analysis.py    # Technical indicators
│       │   ├── portfolio.py             # Portfolio management
│       │   └── alert_system.py          # Price alerts system (uses EmailService)
│       └── templates/
│           └── email/              # Email templates (if any, for future use)
├── tests/
│   ├── __init__.py
│   ├── test_database.py           # Database tests
│   ├── test_technical_analysis.py # Technical analysis tests
│   ├── test_portfolio.py          # Portfolio tests
│   ├── test_email_service.py      # Email service tests
│   ├── test_prediction_service.py # Prediction service tests
│   └── fixtures/                  # Test data fixtures
├── data/
│   ├── stocks.db                  # SQLite database
│   └── users.json                 # User data (if auth.py uses it)
├── docs/
│   └── EMAIL_SETUP.md             # Guide for configuring email notifications for alerts
├── enhanced_app.py                # Enhanced Streamlit application (references PredictionService, AlertSystem)
├── app.py                         # Original application (deprecated or simplified)
├── auth.py                        # Authentication module (may have its own email setup for password resets)
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
streamlit run enhanced_app.py
```

5. **Open your browser to:** `http://localhost:8501`

## 🧪 Testing

Run the comprehensive test suite:
```bash
# Example using unittest:
python -m unittest discover tests
```
(Adjust based on your actual test runner setup, e.g., `pytest tests/`)

## 🛠️ Troubleshooting

### Common Issues

**❓ "Module not found" errors**
- Ensure you're in the project root directory.
- Make sure dependencies are installed: `pip install -r requirements.txt`.
- Verify your `PYTHONPATH` if running scripts from subdirectories.

**❓ "No data available" for stocks**
- Check your internet connection.
- Yahoo Finance service might be temporarily unavailable.

**❓ Email alerts not working**
- Email notifications for alerts are optional and require configuration.
- Please refer to the detailed [Email Setup Guide](docs/EMAIL_SETUP.md) for instructions on setting up the necessary environment variables for the `EmailService`.
- All other application features work without this email setup.

**❓ Database errors**
- The app automatically creates its SQLite database in the `data/` directory.
- If you encounter persistent issues, you can try deleting `data/stocks.db` to reset the database (this will remove all stored portfolio data, alerts, etc.).

## 🔧 Configuration

### Email Configuration for Alerts (Optional)

To enable email notifications for triggered price alerts, you need to configure the `EmailService` by setting specific environment variables.
**For detailed instructions, please see the [Email Setup Guide](docs/EMAIL_SETUP.md).**

This setup is distinct from any email configuration that might be used by the `auth.py` module for features like password resets, which might use different environment variables or methods (e.g., `.streamlit/secrets.toml` if `auth.py` is designed to use Streamlit secrets for that purpose).

### Database Configuration
The application automatically creates a SQLite database in the `data/` directory. No additional configuration is required.

### Stock Data Source
This application uses **Yahoo Finance (yfinance)** which provides free stock data without requiring any API keys or subscriptions.

## 📊 Usage Guide

### Getting Started
1. **Create an account** or login.
2. **Analyze stocks** by entering symbols.
3. **Add to portfolio** to track investments.
4. **Set up alerts** for price movements. If email is configured (see [Email Setup Guide](docs/EMAIL_SETUP.md)), you'll receive notifications.
5. **Explore technical analysis** and **AI-powered predictions**.

### Key Features (Summary)

#### Stock Analysis
- Real-time data, charts, technical indicators, trading signals.

#### Portfolio Management
- Track holdings, performance, allocation. Export data.

#### Price Alerts
- Set price/percentage change alerts. Receive email notifications if configured.

#### Technical Analysis
- 15+ indicators, support/resistance, Fibonacci levels.

#### AI Predictions
- Models: Random Forest, Linear Regression, Gradient Boosting Regressor.
- Uses enhanced feature engineering with technical indicators.

## 📦 Deployment

This app can be deployed on Streamlit Community Cloud. To deploy your own version:

1. Fork this repository.
2. Go to [share.streamlit.io](https://share.streamlit.io).
3. Connect your GitHub account and select your forked repository.
4. Set the main file path to `enhanced_app.py`.
5. Configure any necessary secrets (like those for email, if using) in the Streamlit Cloud settings for your app. Refer to the [Email Setup Guide](docs/EMAIL_SETUP.md) for the required environment variables.
6. Deploy!

**No API keys are required for core stock data functionality.**

## ❓ Frequently Asked Questions

**Q: Do I need any API keys?**  
A: No! The app uses Yahoo Finance which provides free data without requiring API keys for fetching stock data.

**Q: Do I need to set up email for alerts?**
A: No, email notifications for alerts are optional. If you wish to use this feature, refer to the [Email Setup Guide](docs/EMAIL_SETUP.md). The rest of the application functions without it.

**Q: What databases do I need to install?**  
A: None! The app uses SQLite which is built into Python. The database file is created automatically.

**Q: Can I use this for real trading?**  
A: This is for educational and analysis purposes only. Always consult with financial professionals before making investment decisions.

## ⚠️ Disclaimer

This tool is for informational purposes only and should not be considered as financial advice. Always do your own research before making investment decisions.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
```
