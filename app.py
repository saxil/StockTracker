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

# Health check for Streamlit Cloud
try:
    # Import our enhanced modules
    from src.stock_tracker.models.database import Database
    from src.stock_tracker.utils.technical_analysis import TechnicalAnalysis
    from src.stock_tracker.utils.portfolio import Portfolio
    from src.stock_tracker.utils.alert_system import AlertSystem
    
    # Import existing auth system
    from src.stock_tracker.config.auth import UserAuth, init_session_state, login_form, signup_form, show_user_profile, password_reset_form
    
    # Test database connection
    try:
        db = Database()
        st.success("✅ Database connection successful")
    except Exception as e:
        st.error(f"❌ Database connection failed: {str(e)}")
        
except Exception as e:
    st.error(f"❌ Import error: {str(e)}")
    st.stop()

# Page configuration
st.set_page_config(
    page_title="Enhanced Stock Tracker - No API Keys Required",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Modern, Clean UI Styling
st.markdown("""
<style>
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Main app styling */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #1e3c72 0%, #2a5298 100%);
        padding: 1rem;
    }
    
    /* Clean card styling */
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        border: 1px solid #e0e0e0;
        margin-bottom: 1rem;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(45deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
        width: 100%;
        font-size: 14px;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }
    
    /* Sidebar navigation */
    .nav-item {
        background: rgba(255,255,255,0.1);
        margin: 0.5rem 0;
        border-radius: 8px;
        padding: 0.8rem;
        color: white;
        font-weight: 500;
        transition: all 0.2s ease;
    }
    
    .nav-item:hover {
        background: rgba(255,255,255,0.2);
        transform: translateX(5px);
    }
    
    /* Input styling */
    .stTextInput > div > div > input {
        border-radius: 8px;
        border: 2px solid #e0e0e0;
        padding: 0.75rem;
        font-size: 14px;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2);
    }
    
    /* Selectbox styling */
    .stSelectbox > div > div {
        border-radius: 8px;
        border: 2px solid #e0e0e0;
    }
    
    /* Metric styling */
    .metric-container {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        border-left: 4px solid #667eea;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: #f8f9fa;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 500;
    }
    
    .stTabs [aria-selected="true"] {
        background: #667eea;
        color: white;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background: #f8f9fa;
        border-radius: 8px;
        padding: 1rem;
        font-weight: 600;
    }
    
    /* Alert styling */
    .stAlert {
        border-radius: 8px;
        border: none;
        padding: 1rem;
    }
    
    .stSuccess {
        background: linear-gradient(45deg, #56ab2f 0%, #a8e6cf 100%);
        color: white;
    }
    
    .stError {
        background: linear-gradient(45deg, #ff416c 0%, #ff4b2b 100%);
        color: white;
    }
    
    .stInfo {
        background: linear-gradient(45deg, #4facfe 0%, #00f2fe 100%);
        color: white;
    }
    
    /* Dataframe styling */
    .dataframe {
        border-radius: 8px;
        overflow: hidden;
        border: 1px solid #e0e0e0;
    }
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

# Initialize page if not set
if 'current_page' not in st.session_state:
    st.session_state.current_page = "🏠 Dashboard"

# Get current page
page = st.session_state.current_page

# Modern main title with gradient
st.markdown("""
<div style="background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); 
            padding: 2rem; 
            border-radius: 12px; 
            margin-bottom: 2rem;
            text-align: center;">
    <h1 style="color: white; margin: 0; font-size: 2.5rem; font-weight: 700;">
        📈 Stock Tracker Pro
    </h1>
    <p style="color: rgba(255,255,255,0.9); margin: 0.5rem 0 0 0; font-size: 1.1rem;">
        Professional stock analysis with AI-powered insights
    </p>
</div>
""", unsafe_allow_html=True)

# Clean, Modern Sidebar
with st.sidebar:
    # User profile section
    st.markdown("### 👤 User Profile")
    user_info = auth_system.get_user_info(st.session_state.username)
    if user_info:
        st.markdown(f"""
        <div style="background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 8px; margin-bottom: 1.5rem;">
            <div style="color: white; font-size: 16px; font-weight: 600;">Hello, {st.session_state.username}! 👋</div>
            <div style="color: rgba(255,255,255,0.8); font-size: 14px; margin-top: 0.5rem;">
                � {user_info.get('email', 'N/A')}<br>
                📅 Member since {user_info.get('created_at', 'N/A')[:10]}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Navigation
    st.markdown("### 🧭 Navigation")
    nav_options = [
        ("🏠", "Dashboard"),
        ("�", "Stock Analysis"),
        ("💼", "Portfolio"),
        ("🔔", "Alerts"),
        ("�", "Technical Analysis"),
        ("🎯", "Price Prediction")
    ]
    
    for icon, name in nav_options:
        if st.button(f"{icon} {name}", key=f"nav_{name}", use_container_width=True):
            st.session_state.current_page = f"{icon} {name}"
            st.rerun()
    
    st.markdown("---")
    
    # Quick stock lookup
    st.markdown("### 🔍 Quick Stock Lookup")
    with st.container():
        symbol = st.text_input("Enter Symbol", placeholder="e.g., AAPL", label_visibility="collapsed")
        if symbol:
            try:
                ticker = yf.Ticker(symbol.upper())
                info = ticker.info
                price = info.get('currentPrice', 'N/A')
                name = info.get('longName', symbol.upper())
                
                st.markdown(f"""
                <div style="background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 8px; margin: 1rem 0;">
                    <div style="color: white; font-weight: 600; font-size: 14px;">{name[:30]}</div>
                    <div style="color: #4CAF50; font-size: 18px; font-weight: 700;">${price}</div>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"Analyze {symbol.upper()}", use_container_width=True):
                    st.session_state.current_page = "� Stock Analysis"
                    st.session_state.selected_symbol = symbol.upper()
                    st.rerun()
            except:
                st.error("Symbol not found")
    
    st.markdown("---")
    
    # Popular stocks
    st.markdown("### 🔥 Popular Stocks")
    popular = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META"]
    
    cols = st.columns(2)
    for i, stock in enumerate(popular):
        with cols[i % 2]:
            if st.button(stock, key=f"pop_{stock}", use_container_width=True):
                st.session_state.current_page = "� Stock Analysis"
                st.session_state.selected_symbol = stock
                st.rerun()
    
    st.markdown("---")
    
    # Quick actions
    st.markdown("### ⚡ Quick Actions")
    if st.button("🔔 Check Alerts", use_container_width=True):
        alerts = alert_system.get_user_alerts(st.session_state.username)
        if alerts:
            st.success(f"✅ {len(alerts)} active alerts")
        else:
            st.info("📬 No active alerts")
    
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.username = None
        st.rerun()

# Initialize user portfolio
user_portfolio = Portfolio(st.session_state.username, db)

# Page routing
if page == "🏠 Dashboard":
    st.markdown("## 📊 Dashboard Overview")
    
    # Portfolio metrics with improved styling
    portfolio_value = user_portfolio.calculate_portfolio_value()
    active_alerts = alert_system.get_user_alerts(st.session_state.username)
    analysis_history = auth_system.get_analysis_history(st.session_state.username)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                <div style="background: #667eea; color: white; padding: 0.5rem; border-radius: 50%; margin-right: 0.75rem;">💰</div>
                <div style="font-size: 14px; color: #666; font-weight: 600;">PORTFOLIO VALUE</div>
            </div>
            <div style="font-size: 28px; font-weight: 700; color: #2c3e50;">${portfolio_value['total_value']:,.2f}</div>
            <div style="color: {'#27ae60' if portfolio_value['total_gain_loss'] >= 0 else '#e74c3c'}; font-size: 14px; font-weight: 600;">
                {'+' if portfolio_value['total_gain_loss'] >= 0 else ''}${portfolio_value['total_gain_loss']:,.2f}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                <div style="background: #2ecc71; color: white; padding: 0.5rem; border-radius: 50%; margin-right: 0.75rem;">📈</div>
                <div style="font-size: 14px; color: #666; font-weight: 600;">RETURN %</div>
            </div>
            <div style="font-size: 28px; font-weight: 700; color: {'#27ae60' if portfolio_value['total_gain_loss_percent'] >= 0 else '#e74c3c'};">
                {'+' if portfolio_value['total_gain_loss_percent'] >= 0 else ''}{portfolio_value['total_gain_loss_percent']:.2f}%
            </div>
            <div style="color: #7f8c8d; font-size: 14px;">Total return</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                <div style="background: #f39c12; color: white; padding: 0.5rem; border-radius: 50%; margin-right: 0.75rem;">🔔</div>
                <div style="font-size: 14px; color: #666; font-weight: 600;">ACTIVE ALERTS</div>
            </div>
            <div style="font-size: 28px; font-weight: 700; color: #2c3e50;">{len(active_alerts)}</div>
            <div style="color: #7f8c8d; font-size: 14px;">Monitoring stocks</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                <div style="background: #9b59b6; color: white; padding: 0.5rem; border-radius: 50%; margin-right: 0.75rem;">📊</div>
                <div style="font-size: 14px; color: #666; font-weight: 600;">ANALYSES</div>
            </div>
            <div style="font-size: 28px; font-weight: 700; color: #2c3e50;">{len(analysis_history)}</div>
            <div style="color: #7f8c8d; font-size: 14px;">Completed</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Recent activity section
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Recent Analysis")
        if analysis_history:
            recent_analysis = analysis_history[-5:]
            for i, analysis in enumerate(reversed(recent_analysis)):
                st.markdown(f"""
                <div style="background: white; padding: 1rem; border-radius: 8px; margin: 0.5rem 0; border-left: 4px solid #667eea; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <div style="display: flex; justify-content: between; align-items: center;">
                        <div>
                            <div style="font-weight: 600; color: #2c3e50;">{analysis['symbol']}</div>
                            <div style="color: #7f8c8d; font-size: 12px;">{analysis['analysis_type']}</div>
                        </div>
                        <div style="color: #95a5a6; font-size: 11px;">{analysis['timestamp'][:10]}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("🚀 No recent analysis. Start by analyzing some stocks!")
    
    with col2:
        st.markdown("### 💼 Portfolio Overview")
        holdings = user_portfolio.get_detailed_holdings()
        if holdings:
            # Portfolio pie chart
            symbols = [h['symbol'] for h in holdings]
            values = [h['value'] for h in holdings]
            
            fig = px.pie(
                values=values, 
                names=symbols, 
                title="Portfolio Allocation",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig.update_layout(
                height=350,
                showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("💼 Your portfolio is empty. Add some holdings to get started!")
    
    # Quick actions
    st.markdown("### ⚡ Quick Actions")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📊 Analyze Stock", use_container_width=True):
            st.session_state.current_page = "📊 Stock Analysis"
            st.rerun()
    
    with col2:
        if st.button("💼 Manage Portfolio", use_container_width=True):
            st.session_state.current_page = "💼 Portfolio"
            st.rerun()
    
    with col3:
        if st.button("🔔 Set Alert", use_container_width=True):
            st.session_state.current_page = "🔔 Alerts"
            st.rerun()
    
    with col4:
        if st.button("🎯 Price Prediction", use_container_width=True):
            st.session_state.current_page = "🎯 Price Prediction"
            st.rerun()

elif page == "📊 Stock Analysis":
    st.markdown("## 📊 Stock Analysis")
    
    # Stock input section with modern styling
    st.markdown("""
    <div style="background: white; padding: 1.5rem; border-radius: 12px; margin-bottom: 2rem; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        # Use selected symbol if available from sidebar
        default_symbol = st.session_state.get('selected_symbol', 'AAPL')
        symbol = st.text_input("📈 Enter Stock Symbol", value=default_symbol, placeholder="e.g., AAPL, GOOGL, MSFT").upper()
        # Clear selected symbol after use
        if 'selected_symbol' in st.session_state:
            del st.session_state.selected_symbol
    
    with col2:
        period = st.selectbox("📅 Time Period", ["1mo", "3mo", "6mo", "1y", "2y", "5y"], index=2)
    
    with col3:
        analyze_btn = st.button("🔍 Analyze Stock", type="primary", use_container_width=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    if analyze_btn or (symbol and symbol != 'AAPL'):
        try:
            # Fetch stock data with progress
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            status_text.text("🔍 Fetching stock data...")
            progress_bar.progress(25)
            
            ticker = yf.Ticker(symbol)
            hist_data = ticker.history(period=period)
            info = ticker.info
            
            progress_bar.progress(50)
            status_text.text("💾 Storing data...")
            
            # Add stock to database
            db.add_stock(
                symbol=symbol,
                name=info.get('longName', symbol),
                exchange=info.get('exchange'),
                sector=info.get('sector'),
                industry=info.get('industry')
            )
            
            progress_bar.progress(75)
            status_text.text("📊 Running analysis...")
            
            # Store historical data
            for date_idx, row in hist_data.iterrows():
                db.add_stock_data(
                    symbol=symbol,
                    date=date_idx.strftime('%Y-%m-%d'),
                    open_price=row['Open'],
                    high_price=row['High'],
                    low_price=row['Low'],
                    close_price=row['Close'],
                    adj_close_price=row['Close'],
                    volume=int(row['Volume'])
                )
            
            progress_bar.progress(100)
            status_text.text("✅ Analysis complete!")
            
            # Clear progress indicators
            progress_bar.empty()
            status_text.empty()
            
            # Company info header
            current_price = hist_data['Close'].iloc[-1]
            prev_close = hist_data['Close'].iloc[-2] if len(hist_data) > 1 else current_price
            change = current_price - prev_close
            change_pct = (change / prev_close) * 100 if prev_close != 0 else 0
            
            st.markdown(f"""
            <div style="background: white; padding: 2rem; border-radius: 12px; margin-bottom: 2rem; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <h2 style="margin: 0; color: #2c3e50;">{info.get('longName', symbol)} ({symbol})</h2>
                        <div style="display: flex; gap: 2rem; margin-top: 1rem;">
                            <div><strong>Sector:</strong> {info.get('sector', 'N/A')}</div>
                            <div><strong>Industry:</strong> {info.get('industry', 'N/A')}</div>
                            <div><strong>Market Cap:</strong> ${info.get('marketCap', 0):,}</div>
                        </div>
                    </div>
                    <div style="text-align: right;">
                        <div style="font-size: 2rem; font-weight: 700; color: #2c3e50;">${current_price:.2f}</div>
                        <div style="font-size: 1.2rem; color: {'#27ae60' if change >= 0 else '#e74c3c'}; font-weight: 600;">
                            {'+' if change >= 0 else ''}{change:.2f} ({change_pct:+.2f}%)
                        </div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Technical Analysis
            analysis = ta.analyze_stock(hist_data)
            signals = ta.generate_signals(analysis)
            
            if signals:
                st.markdown("### 🎯 Trading Signals")
                
                signal_cols = st.columns(len(signals))
                for i, (signal_type, signal_value) in enumerate(signals.items()):
                    with signal_cols[i]:
                        color = "#27ae60" if "BUY" in signal_value else "#e74c3c" if "SELL" in signal_value else "#95a5a6"
                        st.markdown(f"""
                        <div style="background: white; padding: 1rem; border-radius: 8px; text-align: center; border-left: 4px solid {color}; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                            <div style="font-weight: 600; color: #2c3e50; margin-bottom: 0.5rem;">{signal_type}</div>
                            <div style="color: {color}; font-weight: 700; font-size: 1.1rem;">{signal_value}</div>
                        </div>
                        """, unsafe_allow_html=True)
            
            # Price chart
            st.markdown("### 📈 Price Chart with Technical Indicators")
            
            fig = go.Figure()
            
            # Candlestick chart
            fig.add_trace(go.Candlestick(
                x=hist_data.index,
                open=hist_data['Open'],
                high=hist_data['High'],
                low=hist_data['Low'],
                close=hist_data['Close'],
                name=symbol,
                increasing_line_color='#27ae60',
                decreasing_line_color='#e74c3c'
            ))
            
            # Add technical indicators
            if 'SMA_20' in analysis:
                fig.add_trace(go.Scatter(
                    x=hist_data.index,
                    y=analysis['SMA_20'],
                    mode='lines',
                    name='SMA 20',
                    line=dict(color='#f39c12', width=2)
                ))
            
            if 'SMA_50' in analysis:
                fig.add_trace(go.Scatter(
                    x=hist_data.index,
                    y=analysis['SMA_50'],
                    mode='lines',
                    name='SMA 50',
                    line=dict(color='#3498db', width=2)
                ))
            
            # Bollinger Bands
            if all(key in analysis for key in ['BB_Upper', 'BB_Lower']):
                fig.add_trace(go.Scatter(
                    x=hist_data.index,
                    y=analysis['BB_Upper'],
                    mode='lines',
                    name='BB Upper',
                    line=dict(color='#95a5a6', dash='dash', width=1),
                    showlegend=False
                ))
                fig.add_trace(go.Scatter(
                    x=hist_data.index,
                    y=analysis['BB_Lower'],
                    mode='lines',
                    name='BB Lower',
                    line=dict(color='#95a5a6', dash='dash', width=1),
                    fill='tonexty',
                    fillcolor='rgba(149, 165, 166, 0.1)'
                ))
            
            fig.update_layout(
                title=f"{symbol} - Technical Analysis",
                yaxis_title="Price ($)",
                xaxis_title="Date",
                height=600,
                template="plotly_white",
                showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Additional indicators in tabs
            tab1, tab2 = st.tabs(["📊 Momentum Indicators", "📈 Volume Analysis"])
            
            with tab1:
                col1, col2 = st.columns(2)
                
                with col1:
                    if 'RSI' in analysis:
                        fig_rsi = go.Figure()
                        fig_rsi.add_trace(go.Scatter(
                            x=hist_data.index,
                            y=analysis['RSI'],
                            mode='lines',
                            name='RSI',
                            line=dict(color='#9b59b6', width=2)
                        ))
                        fig_rsi.add_hline(y=70, line_dash="dash", line_color="#e74c3c", annotation_text="Overbought")
                        fig_rsi.add_hline(y=30, line_dash="dash", line_color="#27ae60", annotation_text="Oversold")
                        fig_rsi.update_layout(
                            title="RSI (Relative Strength Index)",
                            height=350,
                            template="plotly_white",
                            yaxis=dict(range=[0, 100])
                        )
                        st.plotly_chart(fig_rsi, use_container_width=True)
                
                with col2:
                    if all(key in analysis for key in ['MACD', 'MACD_Signal']):
                        fig_macd = go.Figure()
                        fig_macd.add_trace(go.Scatter(
                            x=hist_data.index,
                            y=analysis['MACD'],
                            mode='lines',
                            name='MACD',
                            line=dict(color='#2c3e50', width=2)
                        ))
                        fig_macd.add_trace(go.Scatter(
                            x=hist_data.index,
                            y=analysis['MACD_Signal'],
                            mode='lines',
                            name='Signal',
                            line=dict(color='#e74c3c', width=2)
                        ))
                        if 'MACD_Histogram' in analysis:
                            fig_macd.add_trace(go.Bar(
                                x=hist_data.index,
                                y=analysis['MACD_Histogram'],
                                name='Histogram',
                                marker_color='#34495e'
                            ))
                        fig_macd.update_layout(
                            title="MACD",
                            height=350,
                            template="plotly_white"
                        )
                        st.plotly_chart(fig_macd, use_container_width=True)
            
            with tab2:
                # Volume chart
                fig_vol = go.Figure()
                fig_vol.add_trace(go.Bar(
                    x=hist_data.index,
                    y=hist_data['Volume'],
                    name='Volume',
                    marker_color='#3498db'
                ))
                
                fig_vol.update_layout(
                    title="Volume Analysis",
                    yaxis_title="Volume",
                    xaxis_title="Date",
                    height=350,
                    template="plotly_white"
                )
                st.plotly_chart(fig_vol, use_container_width=True)
            
            # Save analysis
            db.save_analysis(
                username=st.session_state.username,
                symbol=symbol,
                analysis_type="Technical Analysis",
                parameters=json.dumps({"period": period}),
                results=json.dumps(signals)
            )
            
            auth_system.add_analysis_history(st.session_state.username, symbol, "Technical Analysis")
            
        except Exception as e:
            st.error(f"❌ Error analyzing {symbol}: {str(e)}")
            st.info("💡 Please check if the symbol is correct and try again.")

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

# Quick actions
if st.sidebar.button("🔍 Check Alerts", use_container_width=True):
    with st.spinner("Checking alerts..."):
        triggered = alert_system.check_alerts()
        if triggered:
            st.sidebar.success(f"✅ {len(triggered)} alerts triggered!")
        else:
            st.sidebar.info("📬 No alerts triggered")

if st.sidebar.button("💡 Quick Tips", use_container_width=True):
    tips = [
        "💰 Diversify your portfolio across sectors",
        "📊 Use technical indicators for better timing",
        "🎯 Set realistic price targets",
        "⏰ Review your alerts regularly",
        "📈 Track long-term trends"
    ]
    import random
    st.sidebar.info(random.choice(tips))

# Simple footer
st.sidebar.markdown("---")
st.sidebar.markdown("""
<div style="text-align: center; color: #666; font-size: 12px; margin: 20px 0;">
    📈 Stock Tracker v2.0<br>
    Built with Streamlit
</div>
""", unsafe_allow_html=True)
