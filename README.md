# Stock Analysis Tool

A comprehensive stock analysis tool built with Streamlit that provides real-time stock data, technical analysis, and machine learning-powered price predictions.

## 🚀 Live Demo

Visit the live application: [Stock Analysis Tool](https://your-app-name.streamlit.app)

## 📋 Features

- **Real-time Stock Data**: Fetch current and historical stock prices using Yahoo Finance
- **Interactive Charts**: Beautiful, interactive charts powered by Plotly
- **Technical Analysis**: Moving averages, RSI, MACD, and other technical indicators
- **Price Prediction**: Machine learning models for stock price forecasting
- **User Authentication**: Secure login system with user profiles
- **Favorites System**: Save and quickly access your favorite stocks
- **Email Alerts**: Get notified about significant price movements
- **Data Export**: Download historical data as CSV files

## 🛠️ Technologies Used

- **Streamlit** - Web application framework
- **Yahoo Finance API** - Stock data source
- **Plotly** - Interactive visualizations
- **scikit-learn** - Machine learning models
- **Pandas** - Data manipulation
- **NumPy** - Numerical computing

## 🏃‍♂️ Running Locally

1. Clone the repository:
```bash
git clone https://github.com/yourusername/StockTracker.git
cd StockTracker
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
streamlit run app.py
```

4. Open your browser to `http://localhost:8501`

## 📦 Deployment

This app is deployed on Streamlit Community Cloud. To deploy your own version:

1. Fork this repository
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub account
4. Select your forked repository
5. Set the main file path to `app.py`
6. Deploy!

## 🔧 Configuration

The app uses environment variables for sensitive data. Create a `.streamlit/secrets.toml` file for local development:

```toml
[email]
GMAIL_EMAIL = "your-email@gmail.com"
GMAIL_APP_PASSWORD = "your-app-password"
```

## 📊 Popular Stock Symbols

Try these popular symbols in the app:
- **AAPL** - Apple Inc.
- **GOOGL** - Alphabet Inc.
- **MSFT** - Microsoft Corporation
- **TSLA** - Tesla Inc.
- **AMZN** - Amazon.com Inc.
- **NVDA** - NVIDIA Corporation

## ⚠️ Disclaimer

This tool is for informational purposes only and should not be considered as financial advice. Always do your own research before making investment decisions.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
