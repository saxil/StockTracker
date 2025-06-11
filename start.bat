@echo off
REM Simple startup script for Stock Tracker on Windows

echo 🚀 Starting Stock Tracker Application
echo =====================================

echo ✅ Using Yahoo Finance (no API keys required)
echo ✅ SQLite database (no external database needed)
echo ℹ️  Email alerts are optional

echo.
echo 📊 Starting Streamlit application...

REM Check if enhanced_app.py exists, otherwise use main.py
if exist "enhanced_app.py" (
    echo 🔧 Running enhanced application...
    streamlit run enhanced_app.py
) else if exist "src\stock_tracker\main.py" (
    echo 🔧 Running main application...
    streamlit run src\stock_tracker\main.py
) else (
    echo ❌ Error: No application file found
    echo    Please make sure you're in the correct directory
    pause
    exit /b 1
)
