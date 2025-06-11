#!/bin/bash
# Simple startup script for Stock Tracker

echo "🚀 Starting Stock Tracker Application"
echo "====================================="

echo "✅ Using Yahoo Finance (no API keys required)"
echo "✅ SQLite database (no external database needed)"
echo "ℹ️  Email alerts are optional"

echo ""
echo "📊 Starting Streamlit application..."

# Check if enhanced_app.py exists, otherwise use main.py
if [ -f "enhanced_app.py" ]; then
    echo "🔧 Running enhanced application..."
    streamlit run enhanced_app.py
elif [ -f "src/stock_tracker/main.py" ]; then
    echo "🔧 Running main application..."
    streamlit run src/stock_tracker/main.py
else
    echo "❌ Error: No application file found"
    echo "   Please make sure you're in the correct directory"
    exit 1
fi
