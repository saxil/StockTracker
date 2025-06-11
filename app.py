import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import numpy as np

# Page configuration
st.set_page_config(
    page_title="Stock Analysis Tool",
    page_icon="📈",
    layout="wide"
)

st.title("📈 Stock Analysis Tool")
st.markdown("Enter a stock symbol to analyze financial data from Yahoo Finance")

# Sidebar for user inputs
st.sidebar.header("Stock Analysis Parameters")

# Stock symbol input
stock_symbol = st.sidebar.text_input(
    "Enter Stock Symbol", 
    value="AAPL",
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
                st.header(f"{info.get('longName', stock_symbol)} ({stock_symbol})")
                
                if info.get('longBusinessSummary'):
                    with st.expander("Company Description"):
                        st.write(info['longBusinessSummary'])
                
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
            else:
                st.error("Failed to fetch stock data. Please try again.")
        else:
            st.error(message)
    else:
        st.info("Please enter a stock symbol to begin analysis.")
else:
    # Display initial instructions
    st.info("👈 Enter a stock symbol in the sidebar and click 'Analyze Stock' to get started!")
    
    # Display sample information
    st.markdown("""
    ### Features:
    - **Real-time Data**: Fetches current stock data from Yahoo Finance
    - **Interactive Charts**: Candlestick price charts and volume analysis
    - **Key Metrics**: P/E ratio, market cap, dividend yield, and more
    - **Historical Data**: Detailed historical price and volume data
    - **CSV Export**: Download historical data for further analysis
    
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
