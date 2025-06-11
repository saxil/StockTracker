import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error
import warnings
warnings.filterwarnings('ignore')

# Import authentication system
from auth import UserAuth, init_session_state, login_form, signup_form, show_user_profile, password_reset_form

# Page configuration
st.set_page_config(
    page_title="Stock Analysis Tool - No API Keys Required",
    page_icon="📈",
    layout="wide"
)

# Initialize authentication system
init_session_state()
auth_system = UserAuth()

# Check if user is authenticated
if not st.session_state.authenticated:
    st.title("📈 Stock Analysis Tool")
    st.info("🚀 **No API keys required!** This app uses free Yahoo Finance data.")
    st.markdown("**Please login or create an account to access the stock analysis features**")
    
    # Show appropriate form based on session state
    if st.session_state.show_signup:
        signup_form(auth_system)
    elif st.session_state.show_reset:
        password_reset_form(auth_system)
    else:
        login_form(auth_system)
    
    # Stop execution here if not authenticated
    st.stop()

# User is authenticated - show the main application
st.title("📈 Stock Analysis Tool")
st.markdown("Analyze financial data from Yahoo Finance with advanced prediction models")

# Show user profile in sidebar
show_user_profile(auth_system)

# Sidebar for user inputs
st.sidebar.header("Stock Analysis Parameters")

# Quick access to favorite stocks
favorite_stocks = auth_system.get_favorite_stocks(st.session_state.username)
if favorite_stocks:
    st.sidebar.markdown("### ⭐ Favorite Stocks")
    selected_favorite = st.sidebar.selectbox(
        "Quick select from favorites:",
        options=[""] + favorite_stocks,
        format_func=lambda x: "Select a favorite..." if x == "" else x
    )
    if selected_favorite:
        st.session_state.selected_stock = selected_favorite

# Stock symbol input
default_symbol = st.session_state.get('selected_stock', "AAPL")
stock_symbol = st.sidebar.text_input(
    "Enter Stock Symbol", 
    value=default_symbol,
    help="Enter a valid stock ticker symbol (e.g., AAPL, GOOGL, MSFT)"
).upper()

# Time period selection
period_options = {
    "1 Month": "1mo",
    "3 Months": "3mo", 
    "6 Months": "6mo",
    "1 Year": "1y",
    "2 Years": "2y",
    "5 Years": "5y"
}

# Prediction settings
st.sidebar.markdown("---")
st.sidebar.header("Price Prediction")
enable_prediction = st.sidebar.checkbox("Enable Price Prediction", value=False)

prediction_days = 30
prediction_model = "LSTM"

if enable_prediction:
    prediction_days = st.sidebar.slider(
        "Prediction Days", 
        min_value=7, 
        max_value=90, 
        value=30,
        help="Number of days to predict into the future"
    )
    
    prediction_model = st.sidebar.selectbox(
        "Prediction Model",
        options=["Random Forest", "Linear Regression"],
        index=0,
        help="Choose the machine learning model for predictions"
    )

selected_period = st.sidebar.selectbox(
    "Select Time Period",
    options=list(period_options.keys()),
    index=3  # Default to 1 Year
)

# Analyze button
analyze_button = st.sidebar.button("Analyze Stock", type="primary")

def validate_stock_symbol(symbol):
    """Validate if stock symbol exists and has data"""
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        # Check if ticker has basic information
        if not info or 'symbol' not in info:
            return False, f"Stock symbol '{symbol}' not found"
        
        # Try to get some recent data
        hist = ticker.history(period="5d")
        if hist.empty:
            return False, f"No historical data available for '{symbol}'"
            
        return True, "Valid symbol"
    except Exception as e:
        return False, f"Error validating symbol: {str(e)}"

def get_stock_data(symbol, period):
    """Fetch comprehensive stock data"""
    try:
        ticker = yf.Ticker(symbol)
        
        # Get historical data
        hist_data = ticker.history(period=period_options[period])
        
        # Get stock info
        info = ticker.info
        
        # Get financial data
        try:
            financials = ticker.financials
            balance_sheet = ticker.balance_sheet
            cash_flow = ticker.cashflow
        except:
            financials = pd.DataFrame()
            balance_sheet = pd.DataFrame()
            cash_flow = pd.DataFrame()
        
        return {
            'history': hist_data,
            'info': info,
            'financials': financials,
            'balance_sheet': balance_sheet,
            'cash_flow': cash_flow
        }
    except Exception as e:
        st.error(f"Error fetching data: {str(e)}")
        return None

def format_large_number(num):
    """Format large numbers for display"""
    if pd.isna(num) or num is None:
        return "N/A"
    
    try:
        num = float(num)
        if abs(num) >= 1e12:
            return f"${num/1e12:.2f}T"
        elif abs(num) >= 1e9:
            return f"${num/1e9:.2f}B"
        elif abs(num) >= 1e6:
            return f"${num/1e6:.2f}M"
        elif abs(num) >= 1e3:
            return f"${num/1e3:.2f}K"
        else:
            return f"${num:.2f}"
    except:
        return "N/A"

def create_price_chart(hist_data, symbol):
    """Create interactive price chart"""
    fig = go.Figure()
    
    # Add candlestick chart
    fig.add_trace(go.Candlestick(
        x=hist_data.index,
        open=hist_data['Open'],
        high=hist_data['High'],
        low=hist_data['Low'],
        close=hist_data['Close'],
        name=f"{symbol} Price"
    ))
    
    fig.update_layout(
        title=f"{symbol} Stock Price Chart",
        xaxis_title="Date",
        yaxis_title="Price ($)",
        template="plotly_white",
        height=500,
        showlegend=False
    )
    
    return fig

def create_volume_chart(hist_data, symbol):
    """Create volume chart"""
    fig = px.bar(
        x=hist_data.index,
        y=hist_data['Volume'],
        title=f"{symbol} Trading Volume",
        labels={'x': 'Date', 'y': 'Volume'}
    )
    
    fig.update_layout(
        template="plotly_white",
        height=400
    )
    
    return fig

def display_key_metrics(info, hist_data):
    """Display key financial metrics"""
    
    # Calculate additional metrics from historical data
    current_price = hist_data['Close'].iloc[-1] if not hist_data.empty else None
    price_change = (hist_data['Close'].iloc[-1] - hist_data['Close'].iloc[-2]) if len(hist_data) > 1 else 0
    price_change_pct = (price_change / hist_data['Close'].iloc[-2] * 100) if len(hist_data) > 1 and hist_data['Close'].iloc[-2] != 0 else 0
    
    # Create metrics dictionary
    metrics = {
        "Current Price": f"${current_price:.2f}" if current_price else "N/A",
        "Price Change": f"${price_change:.2f} ({price_change_pct:+.2f}%)" if price_change else "N/A",
        "Market Cap": format_large_number(info.get('marketCap')),
        "P/E Ratio": f"{info.get('trailingPE', 'N/A'):.2f}" if info.get('trailingPE') and not pd.isna(info.get('trailingPE')) else "N/A",
        "Forward P/E": f"{info.get('forwardPE', 'N/A'):.2f}" if info.get('forwardPE') and not pd.isna(info.get('forwardPE')) else "N/A",
        "PEG Ratio": f"{info.get('pegRatio', 'N/A'):.2f}" if info.get('pegRatio') and not pd.isna(info.get('pegRatio')) else "N/A",
        "Price to Book": f"{info.get('priceToBook', 'N/A'):.2f}" if info.get('priceToBook') and not pd.isna(info.get('priceToBook')) else "N/A",
        "Dividend Yield": f"{info.get('dividendYield', 0) * 100:.2f}%" if info.get('dividendYield') else "N/A",
        "52 Week High": f"${info.get('fiftyTwoWeekHigh', 'N/A')}" if info.get('fiftyTwoWeekHigh') else "N/A",
        "52 Week Low": f"${info.get('fiftyTwoWeekLow', 'N/A')}" if info.get('fiftyTwoWeekLow') else "N/A",
        "Average Volume": f"{info.get('averageVolume', 'N/A'):,}" if info.get('averageVolume') else "N/A",
        "Beta": f"{info.get('beta', 'N/A'):.2f}" if info.get('beta') and not pd.isna(info.get('beta')) else "N/A"
    }
    
    # Display metrics in columns
    col1, col2, col3, col4 = st.columns(4)
    
    metrics_items = list(metrics.items())
    
    with col1:
        for i in range(0, len(metrics_items), 4):
            if i < len(metrics_items):
                key, value = metrics_items[i]
                st.metric(key, value)
    
    with col2:
        for i in range(1, len(metrics_items), 4):
            if i < len(metrics_items):
                key, value = metrics_items[i]
                st.metric(key, value)
    
    with col3:
        for i in range(2, len(metrics_items), 4):
            if i < len(metrics_items):
                key, value = metrics_items[i]
                st.metric(key, value)
    
    with col4:
        for i in range(3, len(metrics_items), 4):
            if i < len(metrics_items):
                key, value = metrics_items[i]
                st.metric(key, value)

def create_historical_data_table(hist_data):
    """Create formatted historical data table"""
    if hist_data.empty:
        return pd.DataFrame()
    
    # Create a copy and format the data
    table_data = hist_data.copy()
    table_data.index = table_data.index.strftime('%Y-%m-%d')
    
    # Round numerical columns
    for col in ['Open', 'High', 'Low', 'Close', 'Adj Close']:
        if col in table_data.columns:
            table_data[col] = table_data[col].round(2)
    
    # Format volume
    if 'Volume' in table_data.columns:
        table_data['Volume'] = table_data['Volume'].apply(lambda x: f"{x:,}")
    
    return table_data

def create_features_for_prediction(data, lookback_days=60):
    """Create features for machine learning prediction"""
    features = []
    targets = []
    
    # Use closing prices for prediction
    prices = data['Close'].values
    
    for i in range(lookback_days, len(prices)):
        features.append(prices[i-lookback_days:i])
        targets.append(prices[i])
    
    return np.array(features), np.array(targets)



def random_forest_prediction(hist_data, prediction_days=30):
    """Random Forest prediction"""
    try:
        # Prepare features
        data = hist_data.copy()
        data['MA_10'] = data['Close'].rolling(window=10).mean()
        data['MA_30'] = data['Close'].rolling(window=30).mean()
        data['Price_Change'] = data['Close'].pct_change()
        data['Volume_Change'] = data['Volume'].pct_change()
        data['High_Low_Ratio'] = data['High'] / data['Low']
        
        # Create lag features
        for lag in [1, 2, 3, 5, 10]:
            data[f'Close_lag_{lag}'] = data['Close'].shift(lag)
        
        # Drop NaN values
        data = data.dropna()
        
        if len(data) < 30:
            st.warning("Insufficient data for Random Forest prediction.")
            return None, None, None
        
        # Prepare features and target
        feature_columns = ['Open', 'High', 'Low', 'Volume', 'MA_10', 'MA_30', 
                          'Price_Change', 'Volume_Change', 'High_Low_Ratio'] + \
                         [f'Close_lag_{lag}' for lag in [1, 2, 3, 5, 10]]
        
        X = data[feature_columns].values
        y = data['Close'].values
        
        # Split data
        train_size = int(len(X) * 0.8)
        X_train, X_test = X[:train_size], X[train_size:]
        y_train, y_test = y[:train_size], y[train_size:]
        
        # Train model
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        
        # Test predictions
        test_predictions = model.predict(X_test)
        
        # Calculate accuracy metrics
        mae = mean_absolute_error(y_test, test_predictions)
        rmse = np.sqrt(mean_squared_error(y_test, test_predictions))
        
        # Predict future prices
        future_predictions = []
        last_features = X[-1].copy()
        
        for day in range(prediction_days):
            pred = model.predict([last_features])[0]
            future_predictions.append(pred)
            
            # Update features for next prediction (simplified approach)
            # In practice, you'd need actual future data for some features
            last_features[0] = pred  # Open = previous close
            last_features[1] = pred * 1.02  # High estimate
            last_features[2] = pred * 0.98  # Low estimate
            # Volume and other features remain same (simplified)
            
            # Update lag features
            for i, lag in enumerate([1, 2, 3, 5, 10]):
                if lag == 1:
                    last_features[-(len([1, 2, 3, 5, 10])-i)] = pred
        
        return np.array(future_predictions), mae, rmse
        
    except Exception as e:
        st.error(f"Random Forest prediction failed: {str(e)}")
        return None, None, None

def linear_regression_prediction(hist_data, prediction_days=30):
    """Linear Regression prediction"""
    try:
        # Simple linear regression on time series
        data = hist_data['Close'].values
        X = np.arange(len(data)).reshape(-1, 1)
        y = data
        
        # Split data
        train_size = int(len(X) * 0.8)
        X_train, X_test = X[:train_size], X[train_size:]
        y_train, y_test = y[:train_size], y[train_size:]
        
        # Train model
        model = LinearRegression()
        model.fit(X_train, y_train)
        
        # Test predictions
        test_predictions = model.predict(X_test)
        
        # Calculate accuracy metrics
        mae = mean_absolute_error(y_test, test_predictions)
        rmse = np.sqrt(mean_squared_error(y_test, test_predictions))
        
        # Predict future prices
        future_X = np.arange(len(data), len(data) + prediction_days).reshape(-1, 1)
        future_predictions = model.predict(future_X)
        
        return future_predictions, mae, rmse
        
    except Exception as e:
        st.error(f"Linear Regression prediction failed: {str(e)}")
        return None, None, None

def create_prediction_chart(hist_data, predictions, prediction_days, symbol, model_name):
    """Create chart showing historical and predicted prices"""
    fig = go.Figure()
    
    # Historical data
    fig.add_trace(go.Scatter(
        x=hist_data.index,
        y=hist_data['Close'],
        mode='lines',
        name='Historical Price',
        line=dict(color='blue')
    ))
    
    # Predicted data
    if predictions is not None:
        last_date = hist_data.index[-1]
        future_dates = pd.date_range(start=last_date + timedelta(days=1), periods=prediction_days)
        
        fig.add_trace(go.Scatter(
            x=future_dates,
            y=predictions,
            mode='lines+markers',
            name=f'{model_name} Prediction',
            line=dict(color='red', dash='dash'),
            marker=dict(size=4)
        ))
        
        # Add connection line
        fig.add_trace(go.Scatter(
            x=[last_date, future_dates[0]],
            y=[hist_data['Close'].iloc[-1], predictions[0]],
            mode='lines',
            name='Connection',
            line=dict(color='red', dash='dash'),
            showlegend=False
        ))
    
    fig.update_layout(
        title=f"{symbol} Price Prediction using {model_name}",
        xaxis_title="Date",
        yaxis_title="Price ($)",
        template="plotly_white",
        height=500,
        hovermode='x unified'
    )
    
    return fig

# Main application logic
if analyze_button or stock_symbol:
    if stock_symbol:
        # Validate stock symbol
        with st.spinner("Validating stock symbol..."):
            is_valid, message = validate_stock_symbol(stock_symbol)
        
        if is_valid:
            # Fetch stock data
            with st.spinner(f"Fetching data for {stock_symbol}..."):
                stock_data = get_stock_data(stock_symbol, selected_period)
            
            if stock_data:
                hist_data = stock_data['history']
                info = stock_data['info']
                
                # Display company information
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.header(f"{info.get('longName', stock_symbol)} ({stock_symbol})")
                with col2:
                    # Add to favorites button
                    is_favorite = stock_symbol in favorite_stocks
                    if st.button("⭐ Remove from Favorites" if is_favorite else "⭐ Add to Favorites"):
                        if is_favorite:
                            auth_system.remove_favorite_stock(st.session_state.username, stock_symbol)
                            st.success(f"Removed {stock_symbol} from favorites")
                        else:
                            auth_system.add_favorite_stock(st.session_state.username, stock_symbol)
                            st.success(f"Added {stock_symbol} to favorites")
                        st.rerun()
                
                if info.get('longBusinessSummary'):
                    with st.expander("Company Description"):
                        st.write(info['longBusinessSummary'])
                
                # Record this analysis in user's history
                analysis_type = "Price Prediction" if enable_prediction else "Stock Analysis"
                auth_system.add_analysis_history(st.session_state.username, stock_symbol, analysis_type)
                
                # Display key metrics
                st.subheader("Key Financial Metrics")
                display_key_metrics(info, hist_data)
                
                # Display charts
                st.subheader("Stock Price Chart")
                if not hist_data.empty:
                    price_chart = create_price_chart(hist_data, stock_symbol)
                    st.plotly_chart(price_chart, use_container_width=True)
                    
                    # Volume chart
                    st.subheader("Trading Volume")
                    volume_chart = create_volume_chart(hist_data, stock_symbol)
                    st.plotly_chart(volume_chart, use_container_width=True)
                else:
                    st.warning("No historical price data available for the selected period.")
                
                # Historical data table
                st.subheader("Historical Data")
                if not hist_data.empty:
                    table_data = create_historical_data_table(hist_data)
                    st.dataframe(table_data, use_container_width=True)
                    
                    # CSV download functionality
                    csv_data = table_data.to_csv()
                    st.download_button(
                        label=f"Download {stock_symbol} Historical Data as CSV",
                        data=csv_data,
                        file_name=f"{stock_symbol}_historical_data_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv",
                        help="Download the historical stock data as a CSV file"
                    )
                else:
                    st.warning("No historical data available for display.")
                
                # Price Prediction Section
                if enable_prediction and not hist_data.empty:
                    st.subheader("🔮 Price Prediction")
                    
                    # Get predictions based on selected model
                    predictions = None
                    mae = None
                    rmse = None
                    
                    if prediction_model == "Random Forest":
                        predictions, mae, rmse = random_forest_prediction(hist_data, prediction_days)
                    elif prediction_model == "Linear Regression":
                        predictions, mae, rmse = linear_regression_prediction(hist_data, prediction_days)
                    
                    if predictions is not None:
                        # Display prediction metrics
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            st.metric("Model", prediction_model)
                        with col2:
                            st.metric("Prediction Days", prediction_days)
                        with col3:
                            st.metric("MAE", f"${mae:.2f}" if mae else "N/A")
                        with col4:
                            st.metric("RMSE", f"${rmse:.2f}" if rmse else "N/A")
                        
                        # Create and display prediction chart
                        prediction_chart = create_prediction_chart(
                            hist_data, predictions, prediction_days, stock_symbol, prediction_model
                        )
                        st.plotly_chart(prediction_chart, use_container_width=True)
                        
                        # Display prediction summary
                        current_price = hist_data['Close'].iloc[-1]
                        predicted_price = predictions[-1]
                        price_change = predicted_price - current_price
                        price_change_pct = (price_change / current_price) * 100
                        
                        st.markdown("### Prediction Summary")
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric(
                                "Current Price", 
                                f"${current_price:.2f}",
                                help="Most recent closing price"
                            )
                        with col2:
                            st.metric(
                                f"Predicted Price ({prediction_days}d)", 
                                f"${predicted_price:.2f}",
                                delta=f"{price_change_pct:+.2f}%"
                            )
                        with col3:
                            trend = "📈 Bullish" if price_change > 0 else "📉 Bearish" if price_change < 0 else "➡️ Neutral"
                            st.metric("Trend", trend)
                        
                        # Create prediction data table
                        last_date = hist_data.index[-1]
                        future_dates = pd.date_range(start=last_date + timedelta(days=1), periods=prediction_days)
                        
                        prediction_df = pd.DataFrame({
                            'Date': future_dates.strftime('%Y-%m-%d'),
                            'Predicted Price': [f"${p:.2f}" for p in predictions]
                        })
                        
                        with st.expander("View Detailed Predictions"):
                            st.dataframe(prediction_df, use_container_width=True)
                            
                            # CSV download for predictions
                            pred_csv = prediction_df.to_csv(index=False)
                            st.download_button(
                                label=f"Download {stock_symbol} Predictions as CSV",
                                data=pred_csv,
                                file_name=f"{stock_symbol}_predictions_{prediction_model.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.csv",
                                mime="text/csv",
                                help="Download the price predictions as a CSV file"
                            )
                        
                        # Disclaimer
                        st.warning(
                            "⚠️ **Disclaimer**: These predictions are based on historical data and machine learning models. "
                            "Stock prices are inherently unpredictable and subject to many external factors. "
                            "This analysis should not be considered as financial advice. Always consult with financial professionals before making investment decisions."
                        )
                    else:
                        st.error("Unable to generate predictions. Please try a different model or check if there's sufficient historical data.")
            else:
                st.error("Failed to fetch stock data. Please try again.")
        else:
            st.error(message)
    else:
        st.info("Please enter a stock symbol to begin analysis.")
else:
    # Display initial instructions
    st.info("👈 Enter a stock symbol in the sidebar and click 'Analyze Stock' to get started!")
    
    # Show user's analysis history
    analysis_history = auth_system.get_analysis_history(st.session_state.username)
    if analysis_history:
        st.subheader("📊 Your Recent Analysis History")
        
        # Display last 10 analyses
        recent_history = analysis_history[-10:]
        history_df = pd.DataFrame(recent_history)
        
        if not history_df.empty:
            # Format timestamp
            history_df['Date'] = pd.to_datetime(history_df['timestamp']).dt.strftime('%Y-%m-%d %H:%M')
            history_df = history_df[['Date', 'symbol', 'analysis_type']]
            history_df.columns = ['Analysis Date', 'Stock Symbol', 'Analysis Type']
            
            st.dataframe(history_df, use_container_width=True)
            
            # Quick analysis buttons for recent stocks
            if len(recent_history) > 0:
                st.markdown("**Quick Re-analyze:**")
                recent_symbols = list(dict.fromkeys([entry['symbol'] for entry in recent_history[-5:]]))
                cols = st.columns(min(len(recent_symbols), 5))
                
                for i, symbol in enumerate(recent_symbols):
                    with cols[i % 5]:
                        if st.button(f"📈 {symbol}", key=f"quick_{symbol}"):
                            st.session_state.selected_stock = symbol
                            st.rerun()
    
    # Display sample information
    st.markdown("""
    ### Features:
    - **Real-time Data**: Fetches current stock data from Yahoo Finance
    - **Interactive Charts**: Candlestick price charts and volume analysis
    - **Key Metrics**: P/E ratio, market cap, dividend yield, and more
    - **Historical Data**: Detailed historical price and volume data
    - **CSV Export**: Download historical data for further analysis
    - **Price Prediction**: ML-powered stock price forecasting
    - **User Favorites**: Save and quickly access your favorite stocks
    
    ### Popular Stock Symbols to Try:
    - **AAPL** - Apple Inc.
    - **GOOGL** - Alphabet Inc.
    - **MSFT** - Microsoft Corporation
    - **TSLA** - Tesla Inc.
    - **AMZN** - Amazon.com Inc.
    - **NVDA** - NVIDIA Corporation
    """)

# Footer
st.markdown("---")
st.markdown("*Data provided by Yahoo Finance. This tool is for informational purposes only and should not be considered as financial advice.*")
