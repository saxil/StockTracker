"""Enhanced Streamlit application with comprehensive stock tracking features."""

import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta, date
import numpy as np
import json
# Removed: MinMaxScaler, RandomForestRegressor, LinearRegression, mean_absolute_error, mean_squared_error
import warnings
warnings.filterwarnings('ignore')

# Import our enhanced modules
from src.stock_tracker.models.database import Database
from src.stock_tracker.utils.technical_analysis import TechnicalAnalysis
from src.stock_tracker.utils.portfolio import Portfolio
from src.stock_tracker.utils.alert_system import AlertSystem
# Import PredictionService
from src.stock_tracker.services.prediction_service import PredictionService


# Import existing auth system
# Assuming auth.py is in the same directory or PYTHONPATH is set
try:
    from auth import UserAuth, init_session_state, login_form, signup_form, show_user_profile, password_reset_form
except ImportError: # Fallback for environments where auth.py might be in src
    from src.auth import UserAuth, init_session_state, login_form, signup_form, show_user_profile, password_reset_form


# Page configuration
st.set_page_config(
    page_title="Enhanced Stock Tracker", # Simpler title
    page_icon="⭐", # Changed icon
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize systems
@st.cache_resource
def init_systems():
    """Initialize database and analysis systems."""
    db = Database()
    ta = TechnicalAnalysis()
    alert_system = AlertSystem(db) # Pass db instance to AlertSystem
    return db, ta, alert_system

# Initialize authentication and systems
init_session_state()
auth_system = UserAuth()
db, ta, alert_system = init_systems()

# Check authentication
if not st.session_state.authenticated:
    st.title("⭐ Enhanced Stock Tracker")
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
st.title("⭐ Enhanced Stock Tracker") # Added icon
st.markdown("Comprehensive stock analysis with portfolio management, alerts, and advanced technical indicators")

# Show user profile in sidebar
show_user_profile(auth_system)

# Main navigation
st.sidebar.header("🧭 Navigation") # Changed icon
page_options = {
    "🏠 Dashboard": "🏠 Dashboard",
    "📈 Stock Analysis": "📈 Stock Analysis",
    "💼 Portfolio": "💼 Portfolio",
    "🔔 Alerts": "🔔 Alerts",
    "📊 Advanced TA": "📊 Advanced TA", # Renamed from "Technical Analysis"
    "🎯 Price Prediction": "🎯 Price Prediction"
}
page_selection = st.sidebar.selectbox(
    "Select Page",
    list(page_options.keys()), # Use keys for display in selectbox
    format_func=lambda key: page_options[key] # Show value (with icon) in selectbox
)
page = page_selection # Assign selected page


# Initialize user portfolio
user_portfolio = Portfolio(st.session_state.username, db)

# Page routing
if page == "🏠 Dashboard":
    st.header("🏠 Dashboard Overview")
    
    # Top Metrics (already have icons via markdown)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("#### 💼 Portfolio Value")
        portfolio_value = user_portfolio.calculate_portfolio_value()
        delta_value = portfolio_value.get('total_gain_loss')
        delta_str = f"${delta_value:,.2f}" if delta_value is not None else None
        st.metric("", f"${portfolio_value.get('total_value', 0):,.2f}", delta=delta_str)
    with col2:
        st.markdown("#### 🔔 Active Alerts")
        active_alerts = alert_system.get_user_alerts(username=st.session_state.username, status="active")
        st.metric("", len(active_alerts))
    with col3:
        st.markdown("#### 📈 Analyses Performed")
        analysis_history = auth_system.get_analysis_history(st.session_state.username)
        st.metric("", len(analysis_history) if analysis_history else 0)

    with st.container():
        st.markdown("---")
        st.subheader("📊 Recent Analysis")
        if analysis_history and len(analysis_history) > 0:
            recent_analysis_display = sorted(analysis_history, key=lambda x: x['timestamp'], reverse=True)[:5]
            for analysis in recent_analysis_display:
                try:
                    if isinstance(analysis['timestamp'], str):
                        timestamp_str = datetime.fromisoformat(analysis['timestamp']).strftime('%Y-%m-%d %H:%M')
                    else:
                        timestamp_str = analysis['timestamp'].strftime('%Y-%m-%d %H:%M')
                except ValueError:
                    timestamp_str = str(analysis['timestamp'])
                with st.expander(f"{analysis.get('symbol', 'N/A')} - {analysis.get('analysis_type', 'N/A')} ({timestamp_str})"):
                    st.write(f"**Symbol:** {analysis.get('symbol', 'N/A')}")
                    st.write(f"**Type:** {analysis.get('analysis_type', 'N/A')}")
        else:
            st.info("No recent analysis found. Start by analyzing some stocks on the 'Stock Analysis' or 'Price Prediction' pages!")

    with st.container():
        st.markdown("---")
        st.subheader("🍰 Portfolio Overview") # Changed icon to match portfolio page
        holdings = user_portfolio.get_detailed_holdings()
        if holdings:
            symbols = [h['symbol'] for h in holdings if h.get('value') is not None and h.get('value') > 0]
            values = [h['value'] for h in holdings if h.get('value') is not None and h.get('value') > 0]
            if values:
                fig_pie_portfolio = px.pie(values=values, names=symbols, title="Portfolio Allocation by Current Value", hole=0.3)
                fig_pie_portfolio.update_traces(textposition='inside', textinfo='percent+label', insidetextorientation='radial')
                fig_pie_portfolio.update_layout(showlegend=False, title_x=0.5, uniformtext_minsize=10, uniformtext_mode='hide')
                st.plotly_chart(fig_pie_portfolio, use_container_width=True)
            else:
                st.info("No holdings with valid current values to display in the allocation chart.")
        else:
            st.info("Your portfolio is empty. Add some holdings via the 'Portfolio' page to see an overview here!")

elif page == "📈 Stock Analysis":
    st.header("📈 Stock Analysis") # Added icon
    
    col1_sa_input, col2_sa_input = st.columns([3, 1])
    with col1_sa_input:
        symbol = st.text_input("Enter Stock Symbol", value="AAPL", key="sa_symbol").upper()
    with col2_sa_input:
        period = st.selectbox("Period", ["1mo", "3mo", "6mo", "1y", "2y", "5y"], index=3, key="sa_period")
    
    if st.button("🔍 Analyze Stock", type="primary", key="sa_analyze_button"): # Added icon
        if not symbol: st.error("Please enter a stock symbol."); st.stop()
        try:
            # ... (data fetching and db interaction) ...
            with st.spinner(f"Fetching data for {symbol}..."):
                ticker = yf.Ticker(symbol)
                hist_data = ticker.history(period=period)
                info = ticker.info
                if hist_data.empty: st.error(f"No historical data found for {symbol} for period {period}."); st.stop()
                if not info or not info.get('regularMarketPrice'): st.warning(f"Could not retrieve complete information for {symbol}. Some details might be missing.")
            db.add_stock(symbol=symbol, name=info.get('longName', symbol), exchange=info.get('exchange'), sector=info.get('sector'), industry=info.get('industry'))
            for date_idx, row in hist_data.iterrows():
                db.add_stock_data(symbol=symbol, date=date_idx.strftime('%Y-%m-%d'), open_price=row['Open'], high_price=row['High'], low_price=row['Low'], close_price=row['Close'], adj_close_price=row.get('Adj Close', row['Close']), volume=int(row['Volume']))

            st.subheader(f"🏢 {info.get('longName', symbol)} ({symbol})") # Added icon
            if info.get('longBusinessSummary'):
                with st.expander("ℹ️ Company Description"): # Added icon
                    st.write(info['longBusinessSummary'])

            col1_info, col2_info = st.columns([2,1]) # Display key info like sector, industry, market cap
            with col1_info:
                st.markdown(f"**Sector:** {info.get('sector', 'N/A')} | **Industry:** {info.get('industry', 'N/A')}")
                st.markdown(f"**Market Cap:** {f'${info.get_market_cap:,}' if info.get('marketCap') else 'N/A'}") # Corrected typo info.get_market_cap
            with col2_info:
                current_price = hist_data['Close'].iloc[-1]
                prev_close = hist_data['Close'].iloc[-2] if len(hist_data) > 1 else current_price
                change = current_price - prev_close
                change_pct = (change / prev_close) * 100 if prev_close != 0 else 0
                st.metric("Current Price", f"${current_price:.2f}", delta=f"{change_pct:+.2f}%")

            analysis_results = ta.analyze_stock(hist_data.copy())
            signals = ta.generate_signals(analysis_results)

            # Tabs for Technical Analysis details
            tab_overview, tab_rsi, tab_macd, tab_more = st.tabs(["🔍 Overview & Price", "🌊 RSI", "📈 MACD", "📊 More Indicators"])

            with tab_overview:
                st.markdown("#### 📜 Key Financial Metrics & Signals") # Added icon
                # Consider a display_key_metrics function here or select few. For now, signals:
                if signals:
                    st.write("**Trading Signals:**")
                    signal_cols = st.columns(min(len(signals), 4))
                    for i, (signal_type, signal_value) in enumerate(signals.items()):
                        with signal_cols[i % 4]:
                            color = "green" if "BUY" in signal_value else "red" if "SELL" in signal_value else "gray"
                            st.markdown(f"**{signal_type.replace('_', ' ').title()}:** :{color}[{signal_value}]")
                else:
                    st.info("No specific trading signals generated from the current set of indicators.")

                st.markdown("#### 💹 Price Chart") # Added icon
                fig_price_analysis = go.Figure()
                # ... (Price chart logic from previous step - assuming it's good) ...
                fig_price_analysis.add_trace(go.Candlestick(x=hist_data.index, open=hist_data['Open'], high=hist_data['High'],low=hist_data['Low'], close=hist_data['Close'], name=symbol, hovertemplate="<b>Date</b>: %{x|%Y-%m-%d}<br><b>Open</b>: $%{open:.2f}<br><b>High</b>: $%{high:.2f}<br><b>Low</b>: $%{low:.2f}<br><b>Close</b>: $%{close:.2f}<extra></extra>"))
                for key_ta in ['SMA_20', 'SMA_50', 'EMA_20', 'EMA_50']:
                    if key_ta in analysis_results:
                        fig_price_analysis.add_trace(go.Scatter(x=hist_data.index, y=analysis_results[key_ta], mode='lines', name=key_ta, hovertemplate=f"<b>Date</b>: %{{x|%Y-%m-%d}}<br><b>{key_ta}</b>: $ %{{y:.2f}}<extra></extra>"))
                if all(key_ta in analysis_results for key_ta in ['BB_Upper', 'BB_Lower', 'BB_Middle']):
                    fig_price_analysis.add_trace(go.Scatter(x=hist_data.index, y=analysis_results['BB_Upper'], mode='lines', name='BB Upper', line=dict(color='rgba(150,150,150,0.5)', dash='dash'), showlegend=True, hovertemplate="<b>Date</b>: %{x|%Y-%m-%d}<br><b>BB Upper</b>: $%{y:.2f}<extra></extra>"))
                    fig_price_analysis.add_trace(go.Scatter(x=hist_data.index, y=analysis_results['BB_Lower'], mode='lines', name='BB Lower', line=dict(color='rgba(150,150,150,0.5)', dash='dash'), fill='tonexty', fillcolor='rgba(150,150,150,0.1)', showlegend=True, hovertemplate="<b>Date</b>: %{x|%Y-%m-%d}<br><b>BB Lower</b>: $%{y:.2f}<extra></extra>"))
                    fig_price_analysis.add_trace(go.Scatter(x=hist_data.index, y=analysis_results['BB_Middle'], mode='lines', name='BB Middle', line=dict(color='rgba(200,200,200,0.4)', dash='dot'), showlegend=True, hovertemplate="<b>Date</b>: %{x|%Y-%m-%d}<br><b>BB Middle</b>: $%{y:.2f}<extra></extra>"))
                fig_price_analysis.update_layout(title=f"{symbol} Price Chart & Key Moving Averages/Bands", yaxis_title="Price ($)", xaxis_title="Date", height=500, hovermode="x unified", legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
                st.plotly_chart(fig_price_analysis, use_container_width=True)

                # Volume Chart could also go here
                # st.markdown("#### 📊 Volume Chart")
                # ... volume chart logic ...


            with tab_rsi:
                if 'RSI' in analysis_results:
                    fig_rsi_analysis = go.Figure()
                    fig_rsi_analysis.add_trace(go.Scatter(x=hist_data.index, y=analysis_results['RSI'], mode='lines', name='RSI', hovertemplate="<b>Date</b>: %{x|%Y-%m-%d}<br><b>RSI</b>: %{y:.2f}<extra></extra>"))
                    fig_rsi_analysis.add_hline(y=70, line_dash="dash", line_color="red", annotation_text="Overbought (70)")
                    fig_rsi_analysis.add_hline(y=30, line_dash="dash", line_color="green", annotation_text="Oversold (30)")
                    fig_rsi_analysis.update_layout(title="RSI (Relative Strength Index)", xaxis_title="Date", yaxis_title="RSI Value", height=350, hovermode="x unified")
                    st.plotly_chart(fig_rsi_analysis, use_container_width=True)
                else:
                    st.info("RSI data not available.")

            with tab_macd:
                if all(key in analysis_results for key in ['MACD_line', 'MACD_signal']):
                    fig_macd_analysis = go.Figure()
                    # ... (MACD chart logic from previous step) ...
                    fig_macd_analysis.add_trace(go.Scatter(x=hist_data.index, y=analysis_results['MACD_line'], mode='lines', name='MACD Line', hovertemplate="<b>Date</b>: %{x|%Y-%m-%d}<br><b>MACD</b>: %{y:.2f}<extra></extra>"))
                    fig_macd_analysis.add_trace(go.Scatter(x=hist_data.index, y=analysis_results['MACD_signal'], mode='lines', name='Signal Line', hovertemplate="<b>Date</b>: %{x|%Y-%m-%d}<br><b>Signal</b>: %{y:.2f}<extra></extra>"))
                    if 'MACD_hist' in analysis_results: fig_macd_analysis.add_trace(go.Bar(x=hist_data.index, y=analysis_results['MACD_hist'], name='Histogram', hovertemplate="<b>Date</b>: %{x|%Y-%m-%d}<br><b>Histogram</b>: %{y:.2f}<extra></extra>"))
                    fig_macd_analysis.update_layout(title="MACD", xaxis_title="Date", yaxis_title="Value", height=350, hovermode="x unified", legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
                    st.plotly_chart(fig_macd_analysis, use_container_width=True)
                else:
                    st.info("MACD data not available.")

            with tab_more:
                st.markdown("####  Stochastic Oscillator")
                if all(key in analysis_results for key in ['Stoch_K', 'Stoch_D']):
                    fig_stoch_sa = go.Figure()
                    fig_stoch_sa.add_trace(go.Scatter(x=hist_data.index, y=analysis_results['Stoch_K'], mode='lines', name='%K Line', hovertemplate="<b>Date</b>: %{x|%Y-%m-%d}<br><b>%K</b>: %{y:.2f}<extra></extra>"))
                    fig_stoch_sa.add_trace(go.Scatter(x=hist_data.index, y=analysis_results['Stoch_D'], mode='lines', name='%D Line', hovertemplate="<b>Date</b>: %{x|%Y-%m-%d}<br><b>%D</b>: %{y:.2f}<extra></extra>"))
                    fig_stoch_sa.add_hline(y=80, line_dash="dash", line_color="red", annotation_text="Overbought (80)")
                    fig_stoch_sa.add_hline(y=20, line_dash="dash", line_color="green", annotation_text="Oversold (20)")
                    fig_stoch_sa.update_layout(title="Stochastic Oscillator", xaxis_title="Date", yaxis_title="Value", height=300, hovermode="x unified", legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
                    st.plotly_chart(fig_stoch_sa, use_container_width=True)
                else:
                    st.info("Stochastic Oscillator data not available.")

                st.markdown("#### 🛡️ Support & Resistance Levels")
                support_resistance = ta.calculate_support_resistance(hist_data.copy())
                if support_resistance.get('support') or support_resistance.get('resistance'):
                    col_sr1, col_sr2 = st.columns(2)
                    with col_sr1:
                        st.write("**Support Levels:**")
                        for level in support_resistance.get('support', []): st.markdown(f"- ${level:.2f}")
                    with col_sr2:
                        st.write("**Resistance Levels:**")
                        for level in support_resistance.get('resistance', []): st.markdown(f"- ${level:.2f}")
                else:
                    st.info("Support and Resistance levels could not be determined.")


            st.subheader("📋 Historical Data") # Added icon
            # ... (Historical data table logic) ...
            df_display = hist_data[['Open', 'High', 'Low', 'Close', 'Volume']].copy()
            df_display.index = df_display.index.strftime('%Y-%m-%d')
            st.dataframe(df_display.sort_index(ascending=False), use_container_width=True)


            db.save_analysis(username=st.session_state.username, symbol=symbol, analysis_type="Stock Analysis Page", parameters=json.dumps({"period": period}), results=json.dumps(signals if signals else {}))
            auth_system.add_analysis_history(st.session_state.username, symbol, "Stock Analysis")
            
        except Exception as e:
            st.error(f"Error analyzing {symbol}: {str(e)}")
            st.exception(e)

elif page == "💼 Portfolio":
    st.header("💼 Portfolio Management") # Added icon
    
    st.subheader("💰 Portfolio Summary") # Added icon
    portfolio_value = user_portfolio.calculate_portfolio_value()
    col_pf_sum1, col_pf_sum2, col_pf_sum3, col_pf_sum4 = st.columns(4)
    with col_pf_sum1: st.metric("Total Value", f"${portfolio_value.get('total_value',0):,.2f}")
    with col_pf_sum2: st.metric("Total Cost", f"${portfolio_value.get('total_cost',0):,.2f}")
    with col_pf_sum3: st.metric("Gain/Loss", f"${portfolio_value.get('total_gain_loss',0):,.2f}" if portfolio_value.get('total_gain_loss') is not None else "N/A")
    with col_pf_sum4: st.metric("Return %", f"{portfolio_value.get('total_gain_loss_percent',0):+.2f}%" if portfolio_value.get('total_gain_loss_percent') is not None else "N/A")
    
    with st.expander("➕ Add New Holding"): # Icon already there
        # ... (form logic) ...
        col1_form, col2_form, col3_form, col4_form = st.columns(4)
        with col1_form: new_symbol = st.text_input("Symbol", key="new_holding_symbol").upper()
        with col2_form: new_shares = st.number_input("Shares", min_value=0.000001, step=0.000001, format="%.6f", key="new_holding_shares")
        with col3_form: new_price = st.number_input("Purchase Price", min_value=0.01, step=0.01, key="new_holding_price")
        with col4_form: new_date = st.date_input("Purchase Date", value=date.today(), key="new_holding_date")
        if st.button("➕ Add Holding", key="add_holding_button"): # Added icon
            if new_symbol and new_shares > 0 and new_price > 0:
                success = user_portfolio.add_holding(new_symbol, new_shares, new_price, new_date.isoformat())
                if success: st.success(f"Added {new_shares} shares of {new_symbol}"); st.rerun()
                else: st.error("Failed to add holding. Ensure stock symbol is valid and exists in Yahoo Finance.")
            else: st.error("Please fill in all fields correctly.")

    st.subheader("📋 Current Holdings") # Added icon
    holdings = user_portfolio.get_detailed_holdings()
    if holdings:
        holdings_df = pd.DataFrame(holdings)
        # ... (dataframe display logic - consider column_config for Streamlit 1.10+) ...
        column_configs = {
            "symbol": st.column_config.TextColumn("Symbol", help="Stock ticker symbol"),
            "stock_name": st.column_config.TextColumn("Name", width="medium"),
            "shares": st.column_config.NumberColumn("Shares", format="%.6f"),
            "purchase_price": st.column_config.NumberColumn("Purchase Price", format="$%.2f"),
            "current_price": st.column_config.NumberColumn("Current Price", format="$%.2f"),
            "cost": st.column_config.NumberColumn("Total Cost", format="$%.2f"),
            "value": st.column_config.NumberColumn("Current Value", format="$%.2f"),
            "gain_loss": st.column_config.NumberColumn("Gain/Loss", format="$%.2f"),
            "gain_loss_percent": st.column_config.NumberColumn("Return %", format="%.2f%%"),
        }
        st.dataframe(holdings_df[['symbol', 'stock_name', 'shares', 'purchase_price', 'current_price', 'cost', 'value', 'gain_loss', 'gain_loss_percent']],
                       column_config=column_configs, use_container_width=True, hide_index=True)

        col1_charts, col2_charts = st.columns(2)
        with col1_charts:
            st.markdown("#### 🍰 Portfolio Allocation") # Added icon
            allocation = user_portfolio.get_portfolio_allocation()
            # ... (pie chart logic) ...
            if allocation:
                valid_alloc_values = [v for v in allocation.values() if v is not None and v > 0]
                valid_alloc_names = [k for k, v in allocation.items() if v is not None and v > 0]
                if valid_alloc_values:
                    fig_alloc = px.pie(values=valid_alloc_values, names=valid_alloc_names, title="Allocation by Current Value", hole=0.3) # Removed title from here
                    fig_alloc.update_traces(textposition='inside', textinfo='percent+label')
                    st.plotly_chart(fig_alloc, use_container_width=True)
        with col2_charts:
            st.markdown("#### 🚀 Holdings Performance") # Added icon
            valid_perf_df = holdings_df.dropna(subset=['gain_loss_percent'])
            # ... (bar chart logic) ...
            if not valid_perf_df.empty:
                fig_perf = go.Figure()
                fig_perf.add_trace(go.Bar(x=valid_perf_df['symbol'], y=valid_perf_df['gain_loss_percent'], name='Return %', marker_color=['green' if x > 0 else 'red' for x in valid_perf_df['gain_loss_percent']]))
                fig_perf.update_layout(title="Performance (Return %)", yaxis_title="Return %") # Removed title from here
                st.plotly_chart(fig_perf, use_container_width=True)
        
        if st.button("📥 Export Portfolio to CSV", key="export_portfolio_csv"):
            # ... (export logic) ...
            csv_data = user_portfolio.export_to_csv()
            st.download_button(label="Download CSV", data=csv_data, file_name=f"portfolio_{st.session_state.username}_{datetime.now().strftime('%Y%m%d')}.csv", mime="text/csv")
    else:
        st.info("Your portfolio is empty. Add some holdings to see your portfolio details.")


elif page == "🔔 Alerts":
    st.header("🔔 Price Alerts Management") # Added icon
    with st.expander("➕ Create New Alert"): # Icon already there
        # ... (form logic) ...
        col1_alert, col2_alert, col3_alert = st.columns(3)
        with col1_alert: alert_symbol = st.text_input("Stock Symbol", key="alert_symbol").upper()
        with col2_alert: alert_type = st.selectbox("Alert Type", ["price_above", "price_below", "percent_change"], format_func=lambda x: {"price_above": "Price Above", "price_below": "Price Below", "percent_change": "Percent Change"}[x], key="alert_type")
        with col3_alert:
            if alert_type == "percent_change": threshold = st.number_input("Threshold (%)", min_value=0.1, step=0.1, key="alert_threshold_percent")
            else: threshold = st.number_input("Threshold Price ($)", min_value=0.01, step=0.01, key="alert_threshold_price")
        if st.button("➕ Create Alert", key="create_alert_button"): # Added icon
            # ... (create alert logic) ...
            if alert_symbol and threshold > 0:
                try:
                    ticker_check = yf.Ticker(alert_symbol)
                    if not ticker_check.info or ticker_check.info.get('regularMarketPrice') is None:
                        st.error(f"Invalid or unknown stock symbol: {alert_symbol}. Please check and try again.")
                    else:
                        success, message = alert_system.create_alert(st.session_state.username, alert_symbol, alert_type, threshold)
                        if success: st.success(message); st.rerun()
                        else: st.error(message)
                except Exception as e_ticker:
                    st.error(f"Failed to validate stock symbol {alert_symbol}: {e_ticker}")
            else: st.error("Please fill in all fields correctly (symbol and positive threshold).")


    st.subheader("🔔 Active Alerts") # Added icon
    active_alerts_list = alert_system.get_user_alerts(st.session_state.username, status="active")
    if active_alerts_list:
        for i, alert_item in enumerate(active_alerts_list):
            with st.container():
                cols = st.columns([0.25, 0.25, 0.25, 0.15, 0.1])
                cols[0].markdown(f"**Symbol:** {alert_item['symbol']}")
                cols[1].markdown(f"**Type:** {alert_item['alert_type'].replace('_',' ').title()}")
                threshold_display = f"{alert_item['threshold_value']:.2f}{'%' if alert_item['alert_type'] == 'percent_change' else '$'}"
                cols[2].markdown(f"**Threshold:** {threshold_display}")
                created_at_display = datetime.fromisoformat(alert_item['created_at']).strftime('%Y-%m-%d %H:%M') if isinstance(alert_item['created_at'], str) else alert_item['created_at'].strftime('%Y-%m-%d %H:%M')
                cols[3].markdown(f"*Created: {created_at_display}*")
                if cols[4].button("🗑️ Delete", key=f"delete_alert_{alert_item['id']}", help="Delete this alert"):
                    alert_system.delete_alert(alert_item['id'], st.session_state.username); st.rerun()
            if i < len(active_alerts_list) - 1:
                 st.markdown("---") # Use markdown for full-width line
    else: st.info("No active alerts. Create some alerts to monitor your stocks!")
    
    st.subheader("📈 Alert Statistics") # Added icon
    # ... (stats logic) ...
    stats = alert_system.get_alert_statistics(st.session_state.username)
    col1_stats, col2_stats, col3_stats = st.columns(3)
    with col1_stats: st.metric("Active Alerts", stats.get('active_alerts',0))
    with col2_stats: st.metric("Triggered Alerts (All Time)", stats.get('triggered_alerts',0))
    with col3_stats: st.metric("Total Alerts Created", stats.get('total_alerts',0))


elif page == "📊 Advanced TA":
    st.header("📊 Advanced Technical Analysis") # Added icon
    symbol_adv_ta = st.text_input("Enter Stock Symbol for Advanced TA", value="AAPL", key="adv_ta_symbol").upper()
    period_adv_ta = st.selectbox("Analysis Period", ["3mo", "6mo", "1y", "2y", "5y"], index=2, key="adv_ta_period")
    
    if st.button("⚙️ Run Analysis", type="primary", key="run_adv_ta_button"): # Added icon
        # ... (Advanced TA logic) ...
        if not symbol_adv_ta: st.error("Please enter a stock symbol."); st.stop()
        try:
            ticker = yf.Ticker(symbol_adv_ta)
            hist_data = ticker.history(period=period_adv_ta)
            if hist_data.empty: st.error(f"No data available for {symbol_adv_ta} for period {period_adv_ta}."); st.stop()
            
            analysis = ta.analyze_stock(hist_data.copy())
            signals = ta.generate_signals(analysis)
            support_resistance = ta.calculate_support_resistance(hist_data.copy())
            
            st.subheader("🎯 Trading Signals Summary")
            if signals:
                signal_cols_adv_ta = st.columns(min(len(signals), 4))
                for i, (signal_type, signal_value) in enumerate(signals.items()):
                    with signal_cols_adv_ta[i % 4]:
                        color = "green" if "BUY" in signal_value else "red" if "SELL" in signal_value else "gray"
                        st.markdown(f"**{signal_type.replace('_', ' ').title()}:** :{color}[{signal_value}]")
            else: st.info("No definitive trading signals generated based on the current analysis.")

            st.subheader("🛡️ Support & Resistance Levels") # Added icon
            col1_sr, col2_sr = st.columns(2)
            with col1_sr:
                st.write("**Resistance Levels:**")
                for level in support_resistance.get('resistance', []): st.markdown(f"- ${level:.2f}")
            with col2_sr:
                st.write("**Support Levels:**")
                for level in support_resistance.get('support', []): st.markdown(f"- ${level:.2f}")

            high_price = hist_data['High'].max(); low_price = hist_data['Low'].min()
            fib_levels = ta.fibonacci_retracement(high_price, low_price)
            st.subheader("🌀 Fibonacci Retracement Levels")
            fib_cols = st.columns(len(fib_levels) if fib_levels else 1)
            for i, (level, price) in enumerate(fib_levels.items()):
                with fib_cols[i % len(fib_cols)]: st.metric(level, f"${price:.2f}")

            st.subheader("📈 Advanced Technical Indicator Charts")
            tab1, tab2, tab3, tab4 = st.tabs(["💹 Price & Volume", "💨 Momentum", "🌊 Volatility", "📈 Trend"]) # Added icons

            # ... (Chart logic within tabs - assuming previous hovertemplate enhancements are kept) ...
            with tab1:
                fig_price_vwap = go.Figure()
                fig_price_vwap.add_trace(go.Candlestick(x=hist_data.index, open=hist_data['Open'], high=hist_data['High'],low=hist_data['Low'], close=hist_data['Close'], name=symbol_adv_ta, hovertemplate="<b>Date</b>: %{x|%Y-%m-%d}<br><b>Open</b>: $%{open:.2f}<br><b>High</b>: $%{high:.2f}<br><b>Low</b>: $%{low:.2f}<br><b>Close</b>: $%{close:.2f}<extra></extra>"))
                if 'VWAP' in analysis: fig_price_vwap.add_trace(go.Scatter(x=hist_data.index, y=analysis['VWAP'], mode='lines', name='VWAP', line=dict(color='purple'), hovertemplate="<b>Date</b>: %{x|%Y-%m-%d}<br><b>VWAP</b>: $%{y:.2f}<extra></extra>"))
                fig_price_vwap.update_layout(title=f"{symbol_adv_ta} Price Chart with VWAP", xaxis_title="Date", yaxis_title="Price ($)", height=450, hovermode="x unified", legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
                st.plotly_chart(fig_price_vwap, use_container_width=True)
                if 'OBV' in analysis:
                    fig_vol_obv = go.Figure()
                    fig_vol_obv.add_trace(go.Bar(x=hist_data.index, y=hist_data['Volume'], name='Volume', yaxis='y1', hovertemplate="<b>Date</b>: %{x|%Y-%m-%d}<br><b>Volume</b>: %{y:,}<extra></extra>"))
                    fig_vol_obv.add_trace(go.Scatter(x=hist_data.index, y=analysis['OBV'], mode='lines', name='OBV', yaxis='y2', hovertemplate="<b>Date</b>: %{x|%Y-%m-%d}<br><b>OBV</b>: %{y:,}<extra></extra>"))
                    fig_vol_obv.update_layout(title="Volume and On-Balance Volume (OBV)", xaxis_title="Date", yaxis=dict(title="Volume"), yaxis2=dict(title="OBV", overlaying='y', side='right'), height=350, hovermode="x unified", legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
                    st.plotly_chart(fig_vol_obv, use_container_width=True)
            with tab2:
                col_momentum1, col_momentum2 = st.columns(2)
                with col_momentum1:
                    if 'RSI' in analysis:
                        fig_rsi_adv = go.Figure()
                        fig_rsi_adv.add_trace(go.Scatter(x=hist_data.index, y=analysis['RSI'], mode='lines', name='RSI', hovertemplate="<b>Date</b>: %{x|%Y-%m-%d}<br><b>RSI</b>: %{y:.2f}<extra></extra>"))
                        fig_rsi_adv.add_hline(y=70, line_dash="dash", line_color="red", annotation_text="Overbought (70)")
                        fig_rsi_adv.add_hline(y=30, line_dash="dash", line_color="green", annotation_text="Oversold (30)")
                        fig_rsi_adv.update_layout(title="RSI", xaxis_title="Date", yaxis_title="RSI Value", height=300, hovermode="x unified")
                        st.plotly_chart(fig_rsi_adv, use_container_width=True)
                with col_momentum2:
                    if all(key in analysis for key in ['Stoch_K', 'Stoch_D']):
                        fig_stoch_adv = go.Figure()
                        fig_stoch_adv.add_trace(go.Scatter(x=hist_data.index, y=analysis['Stoch_K'], mode='lines', name='%K Line', hovertemplate="<b>Date</b>: %{x|%Y-%m-%d}<br><b>%K</b>: %{y:.2f}<extra></extra>"))
                        fig_stoch_adv.add_trace(go.Scatter(x=hist_data.index, y=analysis['Stoch_D'], mode='lines', name='%D Line', hovertemplate="<b>Date</b>: %{x|%Y-%m-%d}<br><b>%D</b>: %{y:.2f}<extra></extra>"))
                        fig_stoch_adv.add_hline(y=80, line_dash="dash", line_color="red", annotation_text="Overbought (80)")
                        fig_stoch_adv.add_hline(y=20, line_dash="dash", line_color="green", annotation_text="Oversold (20)")
                        fig_stoch_adv.update_layout(title="Stochastic Oscillator", xaxis_title="Date", yaxis_title="Value", height=300, hovermode="x unified", legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
                        st.plotly_chart(fig_stoch_adv, use_container_width=True)
            with tab3:
                if 'ATR' in analysis:
                    fig_atr_adv = go.Figure()
                    fig_atr_adv.add_trace(go.Scatter(x=hist_data.index, y=analysis['ATR'], mode='lines', name='ATR', hovertemplate="<b>Date</b>: %{x|%Y-%m-%d}<br><b>ATR</b>: %{y:.2f}<extra></extra>"))
                    fig_atr_adv.update_layout(title="Average True Range (ATR)", xaxis_title="Date", yaxis_title="ATR Value", height=350, hovermode="x unified")
                    st.plotly_chart(fig_atr_adv, use_container_width=True)
            with tab4:
                if all(key in analysis for key in ['MACD_line', 'MACD_signal']):
                    fig_macd_adv = go.Figure()
                    fig_macd_adv.add_trace(go.Scatter(x=hist_data.index, y=analysis['MACD_line'], mode='lines', name='MACD Line', hovertemplate="<b>Date</b>: %{x|%Y-%m-%d}<br><b>MACD</b>: %{y:.2f}<extra></extra>"))
                    fig_macd_adv.add_trace(go.Scatter(x=hist_data.index, y=analysis['MACD_signal'], mode='lines', name='Signal Line', hovertemplate="<b>Date</b>: %{x|%Y-%m-%d}<br><b>Signal</b>: %{y:.2f}<extra></extra>"))
                    if 'MACD_hist' in analysis: fig_macd_adv.add_trace(go.Bar(x=hist_data.index, y=analysis['MACD_hist'], name='Histogram', hovertemplate="<b>Date</b>: %{x|%Y-%m-%d}<br><b>Histogram</b>: %{y:.2f}<extra></extra>"))
                    fig_macd_adv.update_layout(title="MACD", xaxis_title="Date", yaxis_title="Value", height=400, hovermode="x unified", legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
                    st.plotly_chart(fig_macd_adv, use_container_width=True)

            db.save_analysis(username=st.session_state.username, symbol=symbol_adv_ta, analysis_type="Advanced TA", parameters=json.dumps({"period": period_adv_ta}), results=json.dumps(signals if signals else {}))
            auth_system.add_analysis_history(st.session_state.username, symbol_adv_ta, "Advanced TA")
        except Exception as e:
            st.error(f"Error in Advanced TA for {symbol_adv_ta}: {e}"); st.exception(e)


elif page == "🎯 Price Prediction":
    st.header("🎯 AI-Powered Price Prediction") # Added icon
    
    symbol_pred = st.text_input("Enter Stock Symbol for Prediction", value="AAPL", key="pred_symbol").upper()
    col1_pred_opts, col2_pred_opts = st.columns(2)
    with col1_pred_opts:
        prediction_days = st.slider("Prediction Days", 7, 90, 30, key="pred_days")
    with col2_pred_opts:
        model_type_selected = st.selectbox("Model Type", ["Random Forest", "Linear Regression", "Gradient Boosting Regressor"], key="pred_model_type")
    
    if st.button("🔮 Generate Prediction", type="primary", key="run_pred_button"): # Added icon
        # ... (Prediction logic) ...
        if not symbol_pred: st.error("Please enter a stock symbol."); st.stop()
        try:
            with st.spinner(f"Fetching data for {symbol_pred} and generating prediction using {model_type_selected}..."):
                ticker = yf.Ticker(symbol_pred)
                hist_data = ticker.history(period="3y")
                if hist_data.empty or len(hist_data) < 60: st.error(f"Insufficient historical data for {symbol_pred} (need at least 60 days). Fetched {len(hist_data)} days for '3y' period."); st.stop()
                service = PredictionService(model_type=model_type_selected, prediction_days=prediction_days)
                required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
                if not all(col in hist_data.columns for col in required_cols): st.error(f"Historical data for {symbol_pred} is missing required columns: {required_cols}"); st.stop()
                predictions, mae, rmse = service.train_and_predict(hist_data.copy())

            if predictions is not None and mae is not None and rmse is not None:
                st.subheader(f"📈 Prediction Chart for {symbol_pred} ({model_type_selected})") # Added icon and model type
                res_col1, res_col2, res_col3 = st.columns(3)
                current_price = hist_data['Close'].iloc[-1]
                predicted_price_final = predictions[-1]
                change_pct = ((predicted_price_final - current_price) / current_price) * 100 if current_price != 0 else 0
                with res_col1: st.metric("Model MAE", f"${mae:.2f}" if mae else "N/A")
                with res_col2: st.metric("Model RMSE", f"${rmse:.2f}" if rmse else "N/A")
                with res_col3: st.metric("Predicted Change", f"{change_pct:+.2f}%", help=f"Predicted price in {prediction_days} days: ${predicted_price_final:.2f}")

                fig_pred = go.Figure()
                fig_pred.add_trace(go.Scatter(x=hist_data.index, y=hist_data['Close'], mode='lines', name='Historical Prices', hovertemplate="<b>Date</b>: %{x|%Y-%m-%d}<br><b>Price</b>: $%{y:.2f}<extra></extra>"))
                future_dates = pd.date_range(start=hist_data.index[-1] + pd.Timedelta(days=1), periods=len(predictions))
                fig_pred.add_trace(go.Scatter(x=future_dates, y=predictions, mode='lines', name=f'{model_type_selected} Predictions', line=dict(color='red', dash='dash'), hovertemplate="<b>Date</b>: %{x|%Y-%m-%d}<br><b>Predicted</b>: $%{y:.2f}<extra></extra>"))
                fig_pred.update_layout(title=f"{symbol_pred} Price Prediction ({model_type_selected} - {prediction_days} days)", xaxis_title="Date", yaxis_title="Price ($)", height=500, hovermode="x unified", legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
                st.plotly_chart(fig_pred, use_container_width=True)
                
                with st.expander("📄 View Detailed Predictions"): # Added icon
                    st.subheader("📋 Detailed Predictions") # Added icon
                    pred_df = pd.DataFrame({'Date': future_dates.strftime('%Y-%m-%d'), 'Predicted Price': [f"${p:.2f}" for p in predictions], 'Days Ahead': range(1, len(predictions) + 1)})
                    st.dataframe(pred_df, use_container_width=True)
                
                st.warning("⚠️ **Disclaimer**: These predictions are based on historical data and machine learning models. Stock prices are inherently unpredictable. This is not financial advice.")
                db.save_analysis(username=st.session_state.username, symbol=symbol_pred, analysis_type="Price Prediction", parameters=json.dumps({"model_type": model_type_selected, "prediction_days": prediction_days, "mae": float(mae), "rmse": float(rmse)}), results=json.dumps({"predictions": predictions.tolist(), "dates": future_dates.strftime('%Y-%m-%d').tolist()}))
                auth_system.add_analysis_history(st.session_state.username, symbol_pred, f"Prediction ({model_type_selected})")
            else:
                st.error(f"Could not generate predictions for {symbol_pred} using {model_type_selected}. The model may need more data, or data characteristics might not be suitable.")
        except Exception as e:
            st.error(f"Error generating prediction for {symbol_pred}: {str(e)}"); st.exception(e)

# Footer
st.markdown("---")
st.markdown("""
*Enhanced Stock Tracker - Powered by yfinance, scikit-learn, and advanced technical analysis*
*Disclaimer: This tool is for educational and informational purposes only. Not financial advice.*
""")

# Background Alert Check
if 'last_alert_check' not in st.session_state:
    st.session_state.last_alert_check = datetime.now() - timedelta(minutes=16)

if st.sidebar.button("📡 Check Alerts Manually", help="Manually trigger the alert checking process."): # Changed icon and text
    if (datetime.now() - st.session_state.last_alert_check) > timedelta(seconds=60):
        with st.spinner("Checking alerts..."):
            try:
                triggered_alerts_list = alert_system.check_alerts()
                if triggered_alerts_list:
                    st.sidebar.success(f"Alert check complete. {len(triggered_alerts_list)} alerts triggered and processed.")
                    for triggered_alert_info in triggered_alerts_list:
                        st.toast(f"Alert Triggered: {triggered_alert_info['symbol']} at {triggered_alert_info['current_price_at_trigger']:.2f}", icon="🔔")
                else:
                    st.sidebar.info("Alert check complete. No new alerts triggered.")
            except Exception as e_alert_check:
                st.sidebar.error(f"Error during alert check: {e_alert_check}")
            st.session_state.last_alert_check = datetime.now()
    else:
        st.sidebar.info("Alert check was run recently. Please wait a moment.")

```
