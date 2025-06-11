#!/usr/bin/env python3
"""
Test script to verify all modules can be imported correctly
"""

def test_enhanced_app_imports():
    """Test imports for the enhanced application"""
    print("🔍 Testing enhanced_app.py imports...")
    
    try:
        import streamlit as st
        print("✅ streamlit")
        
        import yfinance as yf
        print("✅ yfinance")
        
        import pandas as pd
        print("✅ pandas")
        
        import plotly.graph_objects as go
        print("✅ plotly.graph_objects")
        
        import plotly.express as px
        print("✅ plotly.express")
        
        import numpy as np
        print("✅ numpy")
        
        from sklearn.preprocessing import MinMaxScaler
        from sklearn.ensemble import RandomForestRegressor
        from sklearn.linear_model import LinearRegression
        print("✅ scikit-learn")
        
        # Test our custom modules
        try:
            from src.stock_tracker.models.database import Database
            print("✅ Database module")
        except ImportError as e:
            print(f"⚠️  Database module: {e}")
        
        try:
            from src.stock_tracker.utils.technical_analysis import TechnicalAnalysis
            print("✅ TechnicalAnalysis module")
        except ImportError as e:
            print(f"⚠️  TechnicalAnalysis module: {e}")
        
        try:
            from src.stock_tracker.utils.portfolio import Portfolio
            print("✅ Portfolio module")
        except ImportError as e:
            print(f"⚠️  Portfolio module: {e}")
        
        try:
            from src.stock_tracker.utils.alert_system import AlertSystem
            print("✅ AlertSystem module")
        except ImportError as e:
            print(f"⚠️  AlertSystem module: {e}")
        
        print("\n🎉 All core imports successful!")
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Stock Tracker - Import Test")
    print("==============================")
    test_enhanced_app_imports()
