#!/usr/bin/env python3
"""
Verification script to confirm Stock Tracker works without API keys
"""

def test_imports():
    """Test if all required modules can be imported"""
    print("🔍 Testing imports...")
    
    try:
        import yfinance as yf
        print("✅ yfinance imported successfully")
    except ImportError as e:
        print(f"❌ yfinance import failed: {e}")
        return False
    
    try:
        import streamlit as st
        print("✅ streamlit imported successfully")
    except ImportError as e:
        print(f"❌ streamlit import failed: {e}")
        return False
    
    try:
        import pandas as pd
        print("✅ pandas imported successfully")
    except ImportError as e:
        print(f"❌ pandas import failed: {e}")
        return False
    
    return True

def test_yahoo_finance():
    """Test if Yahoo Finance works without API keys"""
    print("\n📊 Testing Yahoo Finance data access...")
    
    try:
        import yfinance as yf
        
        # Test fetching data for Apple
        ticker = yf.Ticker("AAPL")
        hist = ticker.history(period="5d")
        
        if not hist.empty:
            print(f"✅ Successfully fetched {len(hist)} days of AAPL data")
            print(f"   Latest close price: ${hist['Close'].iloc[-1]:.2f}")
            return True
        else:
            print("❌ No data returned from Yahoo Finance")
            return False
            
    except Exception as e:
        print(f"❌ Yahoo Finance test failed: {e}")
        return False

def main():
    print("🚀 Stock Tracker - API Key Verification")
    print("=======================================")
    print("Testing if the application works without any API keys...")
    print()
    
    # Test imports
    if not test_imports():
        print("\n❌ Import test failed. Please run: pip install -r requirements.txt")
        return False
    
    # Test Yahoo Finance
    if not test_yahoo_finance():
        print("\n❌ Yahoo Finance test failed.")
        return False
    
    print("\n🎉 SUCCESS! Stock Tracker is ready to use without any API keys!")
    print("\n📋 Summary:")
    print("   ✅ All required packages installed")
    print("   ✅ Yahoo Finance data access working")
    print("   ✅ No API keys required")
    print("   ✅ Ready to run: streamlit run enhanced_app.py")
    
    return True

if __name__ == "__main__":
    main()
