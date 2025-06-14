import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import numpy as np
# Removed unused: MinMaxScaler, RandomForestRegressor, LinearRegression, mean_absolute_error, mean_squared_error
import warnings
warnings.filterwarnings('ignore')

# Import authentication system
from auth import UserAuth, init_session_state, login_form, signup_form, show_user_profile, password_reset_form
# Import PredictionService
from src.stock_tracker.services.prediction_service import PredictionService

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

prediction_days_input = 30 # Renamed to avoid conflict if enable_prediction is false
prediction_model_input = "Random Forest" # Renamed

if enable_prediction:
    prediction_days_input = st.sidebar.slider(
        "Prediction Days", 
        min_value=7, 
        max_value=90, 
        value=30,
        help="Number of days to predict into the future"
    )
    
    prediction_model_input = st.sidebar.selectbox(
        "Prediction Model",
        options=["Random Forest", "Linear Regression", "Gradient Boosting Regressor"], # Updated options
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
        
        if not info or 'symbol' not in info or not info.get('regularMarketPrice'): # Check for a valid market price
            return False, f"Stock symbol '{symbol}' not found or no market data."
        
        hist = ticker.history(period="5d")
        if hist.empty:
            return False, f"No historical data available for '{symbol}'"
            
        return True, "Valid symbol"
    except Exception as e:
        # Check for common yfinance "No data found" error string
        if "No data found for symbol" in str(e) or "No price data found" in str(e): # More specific error check
             return False, f"Stock symbol '{symbol}' not found or no data."
        return False, f"Error validating symbol '{symbol}': {str(e)}"

def get_stock_data(symbol, period):
    """Fetch comprehensive stock data"""
    try:
        ticker = yf.Ticker(symbol)
        hist_data = ticker.history(period=period_options[period])
        if hist_data.empty:
            st.error(f"No historical data found for {symbol} for the period {period}.")
            return None
        info = ticker.info
        if not info.get('longName') and not info.get('shortName'): # Check if info is populated
            st.warning(f"Limited information available for {symbol}. Some metrics might be missing.")

        financials = ticker.financials
        balance_sheet = ticker.balance_sheet
        cash_flow = ticker.cashflow
        
        return {
            'history': hist_data,
            'info': info,
            'financials': financials,
            'balance_sheet': balance_sheet,
            'cash_flow': cash_flow
        }
    except Exception as e:
        st.error(f"Error fetching data for {symbol}: {str(e)}")
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
    
    current_price = hist_data['Close'].iloc[-1] if not hist_data.empty else info.get('currentPrice', info.get('regularMarketPrice'))
    price_change = (hist_data['Close'].iloc[-1] - hist_data['Close'].iloc[-2]) if len(hist_data) > 1 else info.get('regularMarketChange', 0)
    price_change_pct = (price_change / hist_data['Close'].iloc[-2] * 100) if len(hist_data) > 1 and hist_data['Close'].iloc[-2] != 0 else info.get('regularMarketChangePercent', 0) * 100
    
    metrics = {
        "Current Price": f"${current_price:.2f}" if current_price else "N/A",
        "Price Change": f"${price_change:.2f} ({price_change_pct:+.2f}%)" if price_change is not None else "N/A",
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
    
    col1, col2, col3, col4 = st.columns(4)
    metrics_items = list(metrics.items())
    
    for i, (key, value) in enumerate(metrics_items):
        if i % 4 == 0:
            with col1: st.metric(key, value)
        elif i % 4 == 1:
            with col2: st.metric(key, value)
        elif i % 4 == 2:
            with col3: st.metric(key, value)
        else:
            with col4: st.metric(key, value)


def create_historical_data_table(hist_data):
    """Create formatted historical data table"""
    if hist_data.empty:
        return pd.DataFrame()
    
    table_data = hist_data.copy()
    table_data.index = table_data.index.strftime('%Y-%m-%d')
    
    for col in ['Open', 'High', 'Low', 'Close', 'Adj Close']:
        if col in table_data.columns:
            table_data[col] = table_data[col].round(2)
    
    if 'Volume' in table_data.columns:
        table_data['Volume'] = table_data['Volume'].apply(lambda x: f"{x:,}")
    
    return table_data

# Removed: create_features_for_prediction, random_forest_prediction, linear_regression_prediction

def create_prediction_chart(hist_data, predictions, prediction_days, symbol, model_name):
    """Create chart showing historical and predicted prices"""
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=hist_data.index,
        y=hist_data['Close'],
        mode='lines',
        name='Historical Price',
        line=dict(color='blue')
    ))
    
    if predictions is not None and len(predictions) > 0: # Added len check
        last_date = hist_data.index[-1]
        future_dates = pd.date_range(start=last_date + timedelta(days=1), periods=len(predictions)) # Use len(predictions)
        
        fig.add_trace(go.Scatter(
            x=future_dates,
            y=predictions,
            mode='lines+markers',
            name=f'{model_name} Prediction',
            line=dict(color='red', dash='dash'),
            marker=dict(size=4)
        ))
        
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
if analyze_button or stock_symbol: # Allow analysis if symbol is pre-filled (e.g. from favorite)
    if stock_symbol:
        with st.spinner("Validating stock symbol..."):
            is_valid, message = validate_stock_symbol(stock_symbol)
        
        if is_valid:
            with st.spinner(f"Fetching data for {stock_symbol}..."):
                stock_data = get_stock_data(stock_symbol, selected_period)
            
            if stock_data and not stock_data['history'].empty: # Ensure hist_data is not empty
                hist_data = stock_data['history']
                info = stock_data['info']
                
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.header(f"{info.get('longName', stock_symbol)} ({stock_symbol})")
                with col2:
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
                
                analysis_type = "Price Prediction" if enable_prediction else "Stock Analysis"
                auth_system.add_analysis_history(st.session_state.username, stock_symbol, analysis_type)
                
                st.subheader("Key Financial Metrics")
                display_key_metrics(info, hist_data)
                
                st.subheader("Stock Price Chart")
                price_chart = create_price_chart(hist_data, stock_symbol)
                st.plotly_chart(price_chart, use_container_width=True)

                st.subheader("Trading Volume")
                volume_chart = create_volume_chart(hist_data, stock_symbol)
                st.plotly_chart(volume_chart, use_container_width=True)
                
                st.subheader("Historical Data")
                table_data = create_historical_data_table(hist_data)
                st.dataframe(table_data, use_container_width=True)
                
                csv_data = table_data.to_csv()
                st.download_button(
                    label=f"Download {stock_symbol} Historical Data as CSV",
                    data=csv_data,
                    file_name=f"{stock_symbol}_historical_data_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                    help="Download the historical stock data as a CSV file"
                )

                if enable_prediction:
                    st.subheader("🔮 Price Prediction")
                    with st.spinner(f"Generating predictions using {prediction_model_input}..."):
                        # Instantiate PredictionService
                        service = PredictionService(model_type=prediction_model_input, prediction_days=prediction_days_input)
                        # Call the service - pass hist_data that has Open, High, Low, Close, Volume
                        # Ensure hist_data has these columns. yfinance usually provides them.
                        required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
                        if all(col in hist_data.columns for col in required_cols):
                            predictions, mae, rmse = service.train_and_predict(hist_data.copy())
                        else:
                            st.error(f"Historical data for {stock_symbol} is missing required columns for prediction: {required_cols}")
                            predictions, mae, rmse = None, None, None
                    
                    if predictions is not None and mae is not None and rmse is not None:
                        col1, col2, col3, col4 = st.columns(4)
                        with col1: st.metric("Model", prediction_model_input)
                        with col2: st.metric("Prediction Days", prediction_days_input)
                        with col3: st.metric("MAE", f"${mae:.2f}")
                        with col4: st.metric("RMSE", f"${rmse:.2f}")
                        
                        prediction_chart = create_prediction_chart(
                            hist_data, predictions, prediction_days_input, stock_symbol, prediction_model_input
                        )
                        st.plotly_chart(prediction_chart, use_container_width=True)
                        
                        current_price = hist_data['Close'].iloc[-1]
                        predicted_price = predictions[-1]
                        price_change = predicted_price - current_price
                        price_change_pct = (price_change / current_price) * 100 if current_price != 0 else 0
                        
                        st.markdown("### Prediction Summary")
                        col1_sum, col2_sum, col3_sum = st.columns(3)
                        with col1_sum: st.metric("Current Price", f"${current_price:.2f}")
                        with col2_sum: st.metric(f"Predicted Price ({prediction_days_input}d)", f"${predicted_price:.2f}", delta=f"{price_change_pct:+.2f}%")
                        trend = "📈 Bullish" if price_change > 0 else "📉 Bearish" if price_change < 0 else "➡️ Neutral"
                        with col3_sum: st.metric("Trend", trend)
                        
                        last_date = hist_data.index[-1]
                        future_dates = pd.date_range(start=last_date + timedelta(days=1), periods=len(predictions))
                        prediction_df = pd.DataFrame({
                            'Date': future_dates.strftime('%Y-%m-%d'),
                            'Predicted Price': [f"${p:.2f}" for p in predictions]
                        })
                        
                        with st.expander("View Detailed Predictions"):
                            st.dataframe(prediction_df, use_container_width=True)
                            pred_csv = prediction_df.to_csv(index=False)
                            st.download_button(
                                label=f"Download {stock_symbol} Predictions as CSV",
                                data=pred_csv,
                                file_name=f"{stock_symbol}_predictions_{prediction_model_input.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.csv",
                                mime="text/csv"
                            )
                        
                        st.warning(
                            "⚠️ **Disclaimer**: These predictions are based on historical data and machine learning models. "
                            "Stock prices are inherently unpredictable and subject to many external factors. "
                            "This analysis should not be considered as financial advice."
                        )
                    elif enable_prediction : # Only show error if prediction was enabled but failed
                        st.error(f"Unable to generate predictions for {prediction_model_input}. The model may require more data or different data characteristics.")
            elif stock_data is None and not is_valid: # Fetching failed after validation error
                 st.error(message) # Show validation message
            elif stock_data is None or stock_data['history'].empty: # Fetching failed for other reasons
                st.error(f"Could not retrieve valid stock data for {stock_symbol}. Please check the symbol or try again later.")
        else:
            st.error(message) # Validation error message
    else:
        st.info("Please enter a stock symbol to begin analysis.")
else:
    st.info("👈 Enter a stock symbol in the sidebar and click 'Analyze Stock' to get started!")
    
    analysis_history = auth_system.get_analysis_history(st.session_state.username)
    if analysis_history:
        st.subheader("📊 Your Recent Analysis History")
        recent_history = analysis_history[-10:]
        history_df = pd.DataFrame(recent_history)
        
        if not history_df.empty:
            history_df['Date'] = pd.to_datetime(history_df['timestamp']).dt.strftime('%Y-%m-%d %H:%M')
            history_df = history_df[['Date', 'symbol', 'analysis_type']]
            history_df.columns = ['Analysis Date', 'Stock Symbol', 'Analysis Type']
            st.dataframe(history_df, use_container_width=True)
            
            if len(recent_history) > 0:
                st.markdown("**Quick Re-analyze:**")
                recent_symbols = list(dict.fromkeys([entry['symbol'] for entry in recent_history[-5:]]))
                cols = st.columns(min(len(recent_symbols), 5))
                
                for i, symbol_hist in enumerate(recent_symbols): # Renamed symbol to symbol_hist
                    with cols[i % 5]:
                        if st.button(f"📈 {symbol_hist}", key=f"quick_{symbol_hist}"):
                            st.session_state.selected_stock = symbol_hist
                            st.rerun()
    
    st.markdown("""
    ### Features:
    - **Real-time Data**: Fetches current stock data from Yahoo Finance
    - **Interactive Charts**: Candlestick price charts and volume analysis
    - **Key Metrics**: P/E ratio, market cap, dividend yield, and more
    - **Historical Data**: Detailed historical price and volume data
    - **CSV Export**: Download historical data for further analysis
    - **Price Prediction**: ML-powered stock price forecasting (Random Forest, Linear Regression, Gradient Boosting)
    - **User Favorites**: Save and quickly access your favorite stocks
    
    ### Popular Stock Symbols to Try:
    - **AAPL** - Apple Inc.
    - **GOOGL** - Alphabet Inc.
    - **MSFT** - Microsoft Corporation
    - **TSLA** - Tesla Inc.
    - **AMZN** - Amazon.com Inc.
    - **NVDA** - NVIDIA Corporation
    """)

st.markdown("---")
st.markdown("*Data provided by Yahoo Finance. This tool is for informational purposes only and should not be considered as financial advice.*")

```
