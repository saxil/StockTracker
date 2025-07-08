import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta, date
import numpy as np
import json
from sklearn.preprocessing import MinMaxScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error
import warnings
warnings.filterwarnings('ignore')

# Import our enhanced modules
from src.stock_tracker.models.database import Database
from src.stock_tracker.utils.technical_analysis import TechnicalAnalysis
from src.stock_tracker.utils.portfolio import Portfolio
from src.stock_tracker.utils.alert_system import AlertSystem

# Import existing auth system
from src.stock_tracker.config.auth import UserAuth, init_session_state, login_form, signup_form, show_user_profile, password_reset_form

# Page configuration
st.set_page_config(
    page_title="Enhanced Stock Tracker - No API Keys Required",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for enhanced styling
st.markdown("""
<style>
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #1e3c72 0%, #2a5298 100%);
    }
    
    /* Main content area */
    .css-18e3th9 {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Buttons styling */
    .stButton > button {
        background: linear-gradient(45deg, #ff6b6b, #ffa726);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: bold;
        transition: all 0.3s ease;
        box-shadow: 0 2px 10px rgba(0,0,0,0.2);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    }
    
    /* Selectbox styling */
    .stSelectbox > div > div {
        background: rgba(255,255,255,0.1);
        border: 1px solid rgba(255,255,255,0.2);
        border-radius: 8px;
    }
    
    /* Metric cards */
    .metric-card {
        background: rgba(255,255,255,0.1);
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid rgba(255,255,255,0.2);
        backdrop-filter: blur(10px);
    }
    
    /* Sidebar divider */
    .sidebar-divider {
        height: 2px;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
        margin: 1rem 0;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Initialize systems
@st.cache_resource
def init_systems():
    """Initialize database and analysis systems."""
    db = Database()
    ta = TechnicalAnalysis()
    alert_system = AlertSystem(db)
    return db, ta, alert_system

# Initialize authentication and systems
init_session_state()
auth_system = UserAuth()
db, ta, alert_system = init_systems()

# Check authentication
if not st.session_state.authenticated:
    st.title("📈 Enhanced Stock Tracker")
    st.markdown("**Please login or create an account to access the advanced stock tracking features**")
    st.info("🚀 **No API keys required!** This app uses free Yahoo Finance data for all stock analysis.")
    
    if st.session_state.show_signup:
        signup_form(auth_system)
    elif st.session_state.show_reset:
        password_reset_form(auth_system)
    else:
        login_form(auth_system)
    
    st.stop()

# Main application
st.title("📈 Enhanced Stock Tracker")
st.markdown("Comprehensive stock analysis with portfolio management, alerts, and advanced technical indicators")
st.success("🚀 **Ready to use!** No API keys or configuration required - just start analyzing stocks!")

# Show user profile in sidebar
show_user_profile(auth_system)

# Enhanced navigation section
st.sidebar.markdown("""
<div style="background: linear-gradient(135deg, #ff6b6b 0%, #ffa726 100%); 
            padding: 20px; 
            border-radius: 15px; 
            margin-bottom: 20px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);">
    <h3 style="color: white; margin: 0; text-align: center;">
        🧭 Navigation
    </h3>
</div>
""", unsafe_allow_html=True)

# Create navigation with custom styling
navigation_options = [
    ("🏠", "Dashboard", "Your personal stock tracking hub"),
    ("📈", "Stock Analysis", "Analyze individual stocks"),
    ("💼", "Portfolio", "Manage your investments"),
    ("🔔", "Alerts", "Set up price notifications"),
    ("📊", "Technical Analysis", "Advanced charting tools"),
    ("🎯", "Price Prediction", "AI-powered forecasting")
]

# Create a more visual navigation
for emoji, title, description in navigation_options:
    if st.sidebar.button(
        f"{emoji} {title}", 
        key=f"nav_{title.lower().replace(' ', '_')}", 
        use_container_width=True,
        help=description
    ):
        st.session_state.current_page = f"{emoji} {title}"

# Use session state for page selection
if 'current_page' not in st.session_state:
    st.session_state.current_page = "🏠 Dashboard"

page = st.session_state.current_page

# Quick actions section
st.sidebar.markdown("""
<div style="background: rgba(255,255,255,0.05); 
            padding: 15px; 
            border-radius: 10px; 
            margin: 20px 0;">
    <h5 style="margin: 0 0 15px 0; color: #333;">⚡ Quick Actions</h5>
</div>
""", unsafe_allow_html=True)

# Quick stock search
with st.sidebar.expander("🔍 Quick Stock Search", expanded=False):
    quick_symbol = st.text_input("Enter stock symbol", placeholder="e.g., AAPL, GOOGL")
    if quick_symbol:
        try:
            import yfinance as yf
            ticker = yf.Ticker(quick_symbol.upper())
            info = ticker.info
            current_price = info.get('currentPrice', 'N/A')
            company_name = info.get('longName', quick_symbol.upper())
            
            st.markdown(f"""
            <div style="background: rgba(76, 175, 80, 0.1); 
                        padding: 10px; 
                        border-radius: 8px; 
                        margin: 10px 0;">
                <strong>{company_name}</strong><br>
                <span style="font-size: 18px; color: #4CAF50;">${current_price}</span>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"Analyze {quick_symbol.upper()}", key="quick_analyze"):
                st.session_state.current_page = "📈 Stock Analysis"
                st.session_state.quick_symbol = quick_symbol.upper()
                st.rerun()
        except Exception as e:
            st.error(f"Error fetching {quick_symbol}: {str(e)}")

# Popular stocks section
st.sidebar.markdown("""
<div style="background: rgba(255,255,255,0.05); 
            padding: 15px; 
            border-radius: 10px; 
            margin: 20px 0;">
    <h5 style="margin: 0 0 15px 0; color: #333;">🔥 Popular Stocks</h5>
</div>
""", unsafe_allow_html=True)

popular_stocks = ["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN", "META"]
cols = st.sidebar.columns(3)
for i, stock in enumerate(popular_stocks):
    with cols[i % 3]:
        if st.button(stock, key=f"popular_{stock}", use_container_width=True):
            st.session_state.current_page = "📈 Stock Analysis"
            st.session_state.quick_symbol = stock
            st.rerun()

# Initialize user portfolio
user_portfolio = Portfolio(st.session_state.username, db)

# Page routing
if page == "🏠 Dashboard":
    st.header("Dashboard")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Portfolio summary
        portfolio_value = user_portfolio.calculate_portfolio_value()
        st.metric(
            "Portfolio Value", 
            f"${portfolio_value['total_value']:,.2f}",
            delta=f"${portfolio_value['total_gain_loss']:,.2f}"
        )
    
    with col2:
        # Active alerts count
        active_alerts = alert_system.get_user_alerts(st.session_state.username)
        st.metric("Active Alerts", len(active_alerts))
    
    with col3:
        # Analysis history count
        analysis_history = auth_system.get_analysis_history(st.session_state.username)
        st.metric("Analyses Performed", len(analysis_history))
    
    # Recent activity
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Recent Analysis")
        if analysis_history:
            recent_analysis = analysis_history[-5:]
            for analysis in reversed(recent_analysis):
                with st.expander(f"{analysis['symbol']} - {analysis['analysis_type']}"):
                    st.write(f"**Date:** {analysis['timestamp']}")
                    st.write(f"**Symbol:** {analysis['symbol']}")
                    st.write(f"**Type:** {analysis['analysis_type']}")
        else:
            st.info("No recent analysis found. Start by analyzing some stocks!")
    
    with col2:
        st.subheader("💼 Portfolio Overview")
        holdings = user_portfolio.get_detailed_holdings()
        if holdings:
            # Create portfolio pie chart
            symbols = [h['symbol'] for h in holdings]
            values = [h['value'] for h in holdings]
            
            fig = px.pie(
                values=values, 
                names=symbols, 
                title="Portfolio Allocation"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Your portfolio is empty. Add some holdings to get started!")

elif page == "📈 Stock Analysis":
    st.header("Stock Analysis")
    
    # Stock input with quick symbol support
    col1, col2 = st.columns([3, 1])
    with col1:
        # Use quick symbol if available
        default_symbol = st.session_state.get('quick_symbol', 'AAPL')
        symbol = st.text_input("Enter Stock Symbol", value=default_symbol).upper()
        # Clear quick symbol after use
        if 'quick_symbol' in st.session_state:
            del st.session_state.quick_symbol
    with col2:
        period = st.selectbox("Period", ["1mo", "3mo", "6mo", "1y", "2y", "5y"])
    
    if st.button("Analyze Stock", type="primary") or default_symbol != 'AAPL':
        try:
            # Fetch stock data
            with st.spinner(f"Fetching data for {symbol}..."):
                ticker = yf.Ticker(symbol)
                hist_data = ticker.history(period=period)
                info = ticker.info
                
                # Add stock to database
                db.add_stock(
                    symbol=symbol,
                    name=info.get('longName', symbol),
                    exchange=info.get('exchange'),
                    sector=info.get('sector'),
                    industry=info.get('industry')
                )
                
                # Store historical data in database
                for date_idx, row in hist_data.iterrows():
                    db.add_stock_data(
                        symbol=symbol,
                        date=date_idx.strftime('%Y-%m-%d'),
                        open_price=row['Open'],
                        high_price=row['High'],
                        low_price=row['Low'],
                        close_price=row['Close'],
                        adj_close_price=row['Close'],  # Assuming adj close = close for simplicity
                        volume=int(row['Volume'])
                    )
            
            # Display basic info
            col1, col2 = st.columns([2, 1])
            with col1:
                st.subheader(f"{info.get('longName', symbol)} ({symbol})")
                st.write(f"**Sector:** {info.get('sector', 'N/A')}")
                st.write(f"**Industry:** {info.get('industry', 'N/A')}")
                st.write(f"**Market Cap:** ${info.get('marketCap', 0):,}")
            
            with col2:
                current_price = hist_data['Close'].iloc[-1]
                prev_close = hist_data['Close'].iloc[-2] if len(hist_data) > 1 else current_price
                change = current_price - prev_close
                change_pct = (change / prev_close) * 100 if prev_close != 0 else 0
                
                st.metric(
                    "Current Price",
                    f"${current_price:.2f}",
                    delta=f"{change_pct:+.2f}%"
                )
            
            # Technical Analysis
            st.subheader("🔍 Technical Analysis")
            analysis = ta.analyze_stock(hist_data)
            signals = ta.generate_signals(analysis)
            
            # Display signals
            if signals:
                st.write("**Trading Signals:**")
                signal_cols = st.columns(len(signals))
                for i, (signal_type, signal_value) in enumerate(signals.items()):
                    with signal_cols[i]:
                        color = "green" if "BUY" in signal_value else "red" if "SELL" in signal_value else "gray"
                        st.markdown(f"**{signal_type}:** :{color}[{signal_value}]")
            
            # Price chart with technical indicators
            st.subheader("📊 Price Chart with Technical Indicators")
            
            fig = go.Figure()
            
            # Candlestick chart
            fig.add_trace(go.Candlestick(
                x=hist_data.index,
                open=hist_data['Open'],
                high=hist_data['High'],
                low=hist_data['Low'],
                close=hist_data['Close'],
                name=symbol
            ))
            
            # Add moving averages
            if 'SMA_20' in analysis:
                fig.add_trace(go.Scatter(
                    x=hist_data.index,
                    y=analysis['SMA_20'],
                    mode='lines',
                    name='SMA 20',
                    line=dict(color='orange')
                ))
            
            if 'SMA_50' in analysis:
                fig.add_trace(go.Scatter(
                    x=hist_data.index,
                    y=analysis['SMA_50'],
                    mode='lines',
                    name='SMA 50',
                    line=dict(color='blue')
                ))
            
            # Add Bollinger Bands
            if all(key in analysis for key in ['BB_Upper', 'BB_Lower']):
                fig.add_trace(go.Scatter(
                    x=hist_data.index,
                    y=analysis['BB_Upper'],
                    mode='lines',
                    name='BB Upper',
                    line=dict(color='gray', dash='dash'),
                    showlegend=False
                ))
                fig.add_trace(go.Scatter(
                    x=hist_data.index,
                    y=analysis['BB_Lower'],
                    mode='lines',
                    name='BB Lower',
                    line=dict(color='gray', dash='dash'),
                    fill='tonexty',
                    fillcolor='rgba(128,128,128,0.1)'
                ))
            
            fig.update_layout(
                title=f"{symbol} Price Chart with Technical Indicators",
                yaxis_title="Price ($)",
                xaxis_title="Date",
                height=600
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Additional technical indicators
            col1, col2 = st.columns(2)
            
            with col1:
                # RSI
                if 'RSI' in analysis:
                    st.subheader("RSI (Relative Strength Index)")
                    rsi_fig = go.Figure()
                    rsi_fig.add_trace(go.Scatter(
                        x=hist_data.index,
                        y=analysis['RSI'],
                        mode='lines',
                        name='RSI'
                    ))
                    rsi_fig.add_hline(y=70, line_dash="dash", line_color="red", annotation_text="Overbought")
                    rsi_fig.add_hline(y=30, line_dash="dash", line_color="green", annotation_text="Oversold")
                    rsi_fig.update_layout(height=300)
                    st.plotly_chart(rsi_fig, use_container_width=True)
            
            with col2:
                # MACD
                if all(key in analysis for key in ['MACD', 'MACD_Signal']):
                    st.subheader("MACD")
                    macd_fig = go.Figure()
                    macd_fig.add_trace(go.Scatter(
                        x=hist_data.index,
                        y=analysis['MACD'],
                        mode='lines',
                        name='MACD'
                    ))
                    macd_fig.add_trace(go.Scatter(
                        x=hist_data.index,
                        y=analysis['MACD_Signal'],
                        mode='lines',
                        name='Signal'
                    ))
                    macd_fig.update_layout(height=300)
                    st.plotly_chart(macd_fig, use_container_width=True)
            
            # Save analysis to database
            db.save_analysis(
                username=st.session_state.username,
                symbol=symbol,
                analysis_type="Technical Analysis",
                parameters=json.dumps({"period": period}),
                results=json.dumps(signals)
            )
            
            # Record in auth system (for compatibility)
            auth_system.add_analysis_history(st.session_state.username, symbol, "Technical Analysis")
            
        except Exception as e:
            st.error(f"Error analyzing {symbol}: {str(e)}")

elif page == "💼 Portfolio":
    st.header("Portfolio Management")
    
    # Portfolio summary
    portfolio_value = user_portfolio.calculate_portfolio_value()
    performance = user_portfolio.get_performance_summary()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Value", f"${portfolio_value['total_value']:,.2f}")
    with col2:
        st.metric("Total Cost", f"${portfolio_value['total_cost']:,.2f}")
    with col3:
        st.metric("Gain/Loss", f"${portfolio_value['total_gain_loss']:,.2f}")
    with col4:
        st.metric("Return %", f"{portfolio_value['total_gain_loss_percent']:+.2f}%")
    
    # Add new holding
    with st.expander("➕ Add New Holding"):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            new_symbol = st.text_input("Symbol").upper()
        with col2:
            new_shares = st.number_input("Shares", min_value=0.01, step=0.01)
        with col3:
            new_price = st.number_input("Purchase Price", min_value=0.01, step=0.01)
        with col4:
            new_date = st.date_input("Purchase Date", value=date.today())
        
        if st.button("Add Holding"):
            if new_symbol and new_shares > 0 and new_price > 0:
                success = user_portfolio.add_holding(
                    new_symbol, new_shares, new_price, new_date.isoformat()
                )
                if success:
                    st.success(f"Added {new_shares} shares of {new_symbol}")
                    st.rerun()
                else:
                    st.error("Failed to add holding")
            else:
                st.error("Please fill in all fields")
    
    # Current holdings
    st.subheader("Current Holdings")
    holdings = user_portfolio.get_detailed_holdings()
    
    if holdings:
        holdings_df = pd.DataFrame(holdings)
        
        # Format for display
        display_df = holdings_df.copy()
        display_df['purchase_price'] = display_df['purchase_price'].apply(lambda x: f"${x:.2f}")
        display_df['current_price'] = display_df['current_price'].apply(lambda x: f"${x:.2f}")
        display_df['cost'] = display_df['cost'].apply(lambda x: f"${x:.2f}")
        display_df['value'] = display_df['value'].apply(lambda x: f"${x:.2f}")
        display_df['gain_loss'] = display_df['gain_loss'].apply(lambda x: f"${x:.2f}")
        display_df['gain_loss_percent'] = display_df['gain_loss_percent'].apply(lambda x: f"{x:+.2f}%")
        
        st.dataframe(
            display_df[['symbol', 'stock_name', 'shares', 'purchase_price', 'current_price', 'cost', 'value', 'gain_loss', 'gain_loss_percent']],
            use_container_width=True
        )
        
        # Portfolio allocation chart
        col1, col2 = st.columns(2)
        
        with col1:
            allocation = user_portfolio.get_portfolio_allocation()
            if allocation:
                fig = px.pie(
                    values=list(allocation.values()),
                    names=list(allocation.keys()),
                    title="Portfolio Allocation"
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Performance chart
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=holdings_df['symbol'],
                y=holdings_df['gain_loss_percent'],
                name='Return %',
                marker_color=['green' if x > 0 else 'red' for x in holdings_df['gain_loss_percent']]
            ))
            fig.update_layout(title="Holdings Performance", yaxis_title="Return %")
            st.plotly_chart(fig, use_container_width=True)
        
        # Export functionality
        if st.button("📥 Export Portfolio to CSV"):
            csv_data = user_portfolio.export_to_csv()
            st.download_button(
                label="Download CSV",
                data=csv_data,
                file_name=f"portfolio_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    else:
        st.info("Your portfolio is empty. Add some holdings to get started!")

elif page == "🔔 Alerts":
    st.header("Price Alerts")
    
    # Create new alert
    with st.expander("➕ Create New Alert"):
        col1, col2, col3 = st.columns(3)
        with col1:
            alert_symbol = st.text_input("Stock Symbol").upper()
        with col2:
            alert_type = st.selectbox(
                "Alert Type",
                ["price_above", "price_below", "percent_change"],
                format_func=lambda x: {
                    "price_above": "Price Above",
                    "price_below": "Price Below", 
                    "percent_change": "Percent Change"
                }[x]
            )
        with col3:
            if alert_type == "percent_change":
                threshold = st.number_input("Threshold (%)", min_value=0.1, step=0.1)
            else:
                threshold = st.number_input("Threshold Price ($)", min_value=0.01, step=0.01)
        
        if st.button("Create Alert"):
            if alert_symbol and threshold > 0:
                success, message = alert_system.create_alert(
                    st.session_state.username, alert_symbol, alert_type, threshold
                )
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
            else:
                st.error("Please fill in all fields")
    
    # Active alerts
    st.subheader("Active Alerts")
    active_alerts = alert_system.get_user_alerts(st.session_state.username)
    
    if active_alerts:
        for alert in active_alerts:
            with st.container():
                col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
                with col1:
                    st.write(f"**{alert['symbol']}**")
                with col2:
                    alert_type_display = {
                        "price_above": "Price Above",
                        "price_below": "Price Below",
                        "percent_change": "Percent Change"
                    }[alert['alert_type']]
                    st.write(alert_type_display)
                with col3:
                    if alert['alert_type'] == "percent_change":
                        st.write(f"{alert['threshold_value']:.1f}%")
                    else:
                        st.write(f"${alert['threshold_value']:.2f}")
                with col4:
                    if st.button("🗑️", key=f"delete_{alert['id']}"):
                        alert_system.delete_alert(alert['id'])
                        st.rerun()
                st.divider()
    else:
        st.info("No active alerts. Create some alerts to monitor your stocks!")
    
    # Alert statistics
    st.subheader("Alert Statistics")
    stats = alert_system.get_alert_statistics(st.session_state.username)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Active Alerts", stats['active_alerts'])
    with col2:
        st.metric("Triggered Alerts", stats['triggered_alerts'])
    with col3:
        st.metric("Total Alerts", stats['total_alerts'])

elif page == "📊 Technical Analysis":
    st.header("Advanced Technical Analysis")
    
    symbol = st.text_input("Enter Stock Symbol for Technical Analysis", value="AAPL").upper()
    period = st.selectbox("Analysis Period", ["3mo", "6mo", "1y", "2y", "5y"])
    
    if st.button("Run Technical Analysis", type="primary"):
        try:
            ticker = yf.Ticker(symbol)
            hist_data = ticker.history(period=period)
            
            if hist_data.empty:
                st.error("No data available for this symbol")
                st.stop()
            
            # Comprehensive technical analysis
            analysis = ta.analyze_stock(hist_data)
            signals = ta.generate_signals(analysis)
            support_resistance = ta.calculate_support_resistance(hist_data)
            
            # Display signals summary
            st.subheader("🎯 Trading Signals Summary")
            if signals:
                signal_cols = st.columns(len(signals))
                for i, (signal_type, signal_value) in enumerate(signals.items()):
                    with signal_cols[i]:
                        color = "green" if "BUY" in signal_value else "red" if "SELL" in signal_value else "gray"
                        st.markdown(f"**{signal_type}**")
                        st.markdown(f":{color}[{signal_value}]")
            
            # Support and Resistance levels
            st.subheader("📊 Support & Resistance Levels")
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Resistance Levels:**")
                for level in support_resistance.get('resistance', []):
                    st.write(f"${level:.2f}")
            
            with col2:
                st.write("**Support Levels:**")
                for level in support_resistance.get('support', []):
                    st.write(f"${level:.2f}")
            
            # Fibonacci retracement
            high_price = hist_data['High'].max()
            low_price = hist_data['Low'].min()
            fib_levels = ta.fibonacci_retracement(high_price, low_price)
            
            st.subheader("🌀 Fibonacci Retracement Levels")
            fib_cols = st.columns(3)
            for i, (level, price) in enumerate(fib_levels.items()):
                with fib_cols[i % 3]:
                    st.metric(level, f"${price:.2f}")
            
            # Advanced indicators chart
            st.subheader("📈 Advanced Technical Indicators")
            
            # Create subplots for different indicators
            tab1, tab2, tab3, tab4 = st.tabs(["Price & Volume", "Momentum", "Volatility", "Trend"])
            
            with tab1:
                # Price and volume
                fig = go.Figure()
                fig.add_trace(go.Candlestick(
                    x=hist_data.index,
                    open=hist_data['Open'],
                    high=hist_data['High'],
                    low=hist_data['Low'],
                    close=hist_data['Close'],
                    name=symbol
                ))
                
                # Add VWAP if available
                if 'VWAP' in analysis:
                    fig.add_trace(go.Scatter(
                        x=hist_data.index,
                        y=analysis['VWAP'],
                        mode='lines',
                        name='VWAP',
                        line=dict(color='purple')
                    ))
                
                fig.update_layout(title=f"{symbol} Price Chart with VWAP", height=400)
                st.plotly_chart(fig, use_container_width=True)
                
                # Volume with OBV
                if 'OBV' in analysis:
                    fig_vol = go.Figure()
                    fig_vol.add_trace(go.Bar(
                        x=hist_data.index,
                        y=hist_data['Volume'],
                        name='Volume'
                    ))
                    
                    # Add OBV on secondary y-axis
                    fig_vol.add_trace(go.Scatter(
                        x=hist_data.index,
                        y=analysis['OBV'],
                        mode='lines',
                        name='OBV',
                        yaxis='y2'
                    ))
                    
                    fig_vol.update_layout(
                        title="Volume and On-Balance Volume (OBV)",
                        yaxis=dict(title="Volume"),
                        yaxis2=dict(title="OBV", overlaying='y', side='right'),
                        height=300
                    )
                    st.plotly_chart(fig_vol, use_container_width=True)
            
            with tab2:
                # Momentum indicators
                col1, col2 = st.columns(2)
                
                with col1:
                    if 'RSI' in analysis:
                        fig_rsi = go.Figure()
                        fig_rsi.add_trace(go.Scatter(
                            x=hist_data.index,
                            y=analysis['RSI'],
                            mode='lines',
                            name='RSI'
                        ))
                        fig_rsi.add_hline(y=70, line_dash="dash", line_color="red")
                        fig_rsi.add_hline(y=30, line_dash="dash", line_color="green")
                        fig_rsi.update_layout(title="RSI", height=300)
                        st.plotly_chart(fig_rsi, use_container_width=True)
                
                with col2:
                    if all(key in analysis for key in ['Stoch_K', 'Stoch_D']):
                        fig_stoch = go.Figure()
                        fig_stoch.add_trace(go.Scatter(
                            x=hist_data.index,
                            y=analysis['Stoch_K'],
                            mode='lines',
                            name='%K'
                        ))
                        fig_stoch.add_trace(go.Scatter(
                            x=hist_data.index,
                            y=analysis['Stoch_D'],
                            mode='lines',
                            name='%D'
                        ))
                        fig_stoch.add_hline(y=80, line_dash="dash", line_color="red")
                        fig_stoch.add_hline(y=20, line_dash="dash", line_color="green")
                        fig_stoch.update_layout(title="Stochastic Oscillator", height=300)
                        st.plotly_chart(fig_stoch, use_container_width=True)
            
            with tab3:
                # Volatility indicators
                if 'ATR' in analysis:
                    fig_atr = go.Figure()
                    fig_atr.add_trace(go.Scatter(
                        x=hist_data.index,
                        y=analysis['ATR'],
                        mode='lines',
                        name='ATR'
                    ))
                    fig_atr.update_layout(title="Average True Range (ATR)", height=300)
                    st.plotly_chart(fig_atr, use_container_width=True)
            
            with tab4:
                # Trend indicators
                if all(key in analysis for key in ['MACD', 'MACD_Signal', 'MACD_Histogram']):
                    fig_macd = go.Figure()
                    fig_macd.add_trace(go.Scatter(
                        x=hist_data.index,
                        y=analysis['MACD'],
                        mode='lines',
                        name='MACD'
                    ))
                    fig_macd.add_trace(go.Scatter(
                        x=hist_data.index,
                        y=analysis['MACD_Signal'],
                        mode='lines',
                        name='Signal'
                    ))
                    fig_macd.add_trace(go.Bar(
                        x=hist_data.index,
                        y=analysis['MACD_Histogram'],
                        name='Histogram'
                    ))
                    fig_macd.update_layout(title="MACD", height=400)
                    st.plotly_chart(fig_macd, use_container_width=True)
            
            # Save comprehensive analysis
            db.save_analysis(
                username=st.session_state.username,
                symbol=symbol,
                analysis_type="Advanced Technical Analysis",
                parameters=json.dumps({"period": period, "indicators": list(analysis.keys())}),
                results=json.dumps({
                    "signals": signals,
                    "support_resistance": support_resistance,
                    "fibonacci_levels": fib_levels
                })
            )
            
        except Exception as e:
            st.error(f"Error performing technical analysis: {str(e)}")

elif page == "🎯 Price Prediction":
    st.header("AI-Powered Price Prediction")
    
    symbol = st.text_input("Enter Stock Symbol for Prediction", value="AAPL").upper()
    
    col1, col2 = st.columns(2)
    with col1:
        prediction_days = st.slider("Prediction Days", 1, 90, 30)
    with col2:
        model_type = st.selectbox("Model Type", ["Random Forest", "Linear Regression"])
    
    if st.button("Generate Prediction", type="primary"):
        try:
            # Fetch data
            ticker = yf.Ticker(symbol)
            hist_data = ticker.history(period="2y")  # Use 2 years for better prediction
            
            if len(hist_data) < 100:
                st.error("Insufficient data for prediction. Need at least 100 days of historical data.")
                st.stop()
            
            # Prepare features for prediction
            def create_features(data, lookback=60):
                features = []
                targets = []
                
                for i in range(lookback, len(data)):
                    features.append(data[i-lookback:i])
                    targets.append(data[i])
                
                return np.array(features), np.array(targets)
            
            # Use closing prices for prediction
            close_prices = hist_data['Close'].values
            scaler = MinMaxScaler()
            scaled_data = scaler.fit_transform(close_prices.reshape(-1, 1)).flatten()
            
            X, y = create_features(scaled_data)
            
            # Split data
            split_idx = int(len(X) * 0.8)
            X_train, X_test = X[:split_idx], X[split_idx:]
            y_train, y_test = y[:split_idx], y[split_idx:]
            
            # Train model
            with st.spinner("Training prediction model..."):
                if model_type == "Random Forest":
                    model = RandomForestRegressor(n_estimators=100, random_state=42)
                    # Reshape for Random Forest (it expects 2D features)
                    X_train_reshaped = X_train.reshape(X_train.shape[0], -1)
                    X_test_reshaped = X_test.reshape(X_test.shape[0], -1)
                    model.fit(X_train_reshaped, y_train)
                    y_pred = model.predict(X_test_reshaped)
                else:  # Linear Regression
                    model = LinearRegression()
                    X_train_reshaped = X_train.reshape(X_train.shape[0], -1)
                    X_test_reshaped = X_test.reshape(X_test.shape[0], -1)
                    model.fit(X_train_reshaped, y_train)
                    y_pred = model.predict(X_test_reshaped)
                
                # Calculate metrics
                mae = mean_absolute_error(y_test, y_pred)
                rmse = np.sqrt(mean_squared_error(y_test, y_pred))
            
            # Generate future predictions
            last_sequence = scaled_data[-60:]
            predictions = []
            
            for _ in range(prediction_days):
                if model_type == "Random Forest":
                    pred = model.predict(last_sequence.reshape(1, -1))[0]
                else:
                    pred = model.predict(last_sequence.reshape(1, -1))[0]
                
                predictions.append(pred)
                # Update sequence for next prediction
                last_sequence = np.append(last_sequence[1:], pred)
            
            # Scale back predictions
            predictions_scaled = scaler.inverse_transform(np.array(predictions).reshape(-1, 1)).flatten()
            
            # Display results
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Model Accuracy (MAE)", f"${mae:.2f}")
            with col2:
                st.metric("RMSE", f"${rmse:.2f}")
            with col3:
                current_price = hist_data['Close'].iloc[-1]
                predicted_price = predictions_scaled[-1]
                change_pct = ((predicted_price - current_price) / current_price) * 100
                st.metric("Predicted Change", f"{change_pct:+.2f}%")
            
            # Plot predictions
            fig = go.Figure()
            
            # Historical data
            fig.add_trace(go.Scatter(
                x=hist_data.index[-100:],  # Show last 100 days
                y=hist_data['Close'].iloc[-100:],
                mode='lines',
                name='Historical Prices',
                line=dict(color='blue')
            ))
            
            # Predictions
            future_dates = pd.date_range(
                start=hist_data.index[-1] + pd.Timedelta(days=1),
                periods=prediction_days,
                freq='D'
            )
            
            fig.add_trace(go.Scatter(
                x=future_dates,
                y=predictions_scaled,
                mode='lines',
                name=f'{model_type} Predictions',
                line=dict(color='red', dash='dash')
            ))
            
            fig.update_layout(
                title=f"{symbol} Price Prediction ({prediction_days} days)",
                xaxis_title="Date",
                yaxis_title="Price ($)",
                height=500
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Prediction table
            st.subheader("Detailed Predictions")
            pred_df = pd.DataFrame({
                'Date': future_dates.strftime('%Y-%m-%d'),
                'Predicted Price': [f"${p:.2f}" for p in predictions_scaled],
                'Days Ahead': range(1, prediction_days + 1)
            })
            st.dataframe(pred_df, use_container_width=True)
            
            # Disclaimer
            st.warning(
                "⚠️ **Disclaimer**: These predictions are based on historical data and machine learning models. "
                "Stock prices are inherently unpredictable and subject to many external factors. "
                "This analysis should not be considered as financial advice."
            )
            
            # Save prediction analysis
            db.save_analysis(
                username=st.session_state.username,
                symbol=symbol,
                analysis_type="Price Prediction",
                parameters=json.dumps({
                    "model_type": model_type,
                    "prediction_days": prediction_days,
                    "mae": float(mae),
                    "rmse": float(rmse)
                }),
                results=json.dumps({
                    "predictions": predictions_scaled.tolist(),
                    "dates": future_dates.strftime('%Y-%m-%d').tolist()
                })
            )
            
        except Exception as e:
            st.error(f"Error generating prediction: {str(e)}")

# Footer
st.markdown("---")
st.markdown("""
*Enhanced Stock Tracker - Powered by yfinance, scikit-learn, and advanced technical analysis*

**Features:**
- 📊 Comprehensive technical analysis with 15+ indicators
- 💼 Portfolio management with performance tracking
- 🔔 Smart price alerts system
- 🎯 AI-powered price predictions
- 📈 Advanced charting and visualization
- 💾 Persistent data storage with SQLite
- 🚀 **No API keys required** - Uses free Yahoo Finance data

*Disclaimer: This tool is for educational and informational purposes only. Not financial advice.*
""")

# Check alerts in background (simplified)
col1, col2 = st.sidebar.columns([1, 1])
with col1:
    if st.button("🔍 Check Alerts", use_container_width=True):
        with st.spinner("Checking alerts..."):
            triggered = alert_system.check_alerts()
            if triggered:
                st.sidebar.success(f"✅ {len(triggered)} alerts triggered!")
            else:
                st.sidebar.info("📬 No alerts triggered")

with col2:
    if st.button("💡 Quick Tips", use_container_width=True):
        tips = [
            "💰 Diversify your portfolio across sectors",
            "📊 Use technical indicators for better timing",
            "🎯 Set realistic price targets",
            "⏰ Review your alerts regularly",
            "📈 Track long-term trends"
        ]
        import random
        st.sidebar.info(random.choice(tips))

# Market status indicator
st.sidebar.markdown("""
<div style="background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%); 
            padding: 15px; 
            border-radius: 10px; 
            margin: 20px 0;
            text-align: center;">
    <h5 style="color: white; margin: 0;">📊 Market Status</h5>
    <p style="color: white; margin: 5px 0; font-size: 14px;">
        Live data from Yahoo Finance
    </p>
</div>
""", unsafe_allow_html=True)

# Footer with app info
st.sidebar.markdown("""
<div style="background: rgba(255,255,255,0.02); 
            padding: 15px; 
            border-radius: 10px; 
            margin-top: 30px;
            border-top: 1px solid rgba(255,255,255,0.1);">
    <p style="text-align: center; color: #666; font-size: 12px; margin: 0;">
        📈 Stock Tracker v2.0<br>
        Built with ❤️ using Streamlit
    </p>
</div>
""", unsafe_allow_html=True)
