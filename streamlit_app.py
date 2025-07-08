#!/usr/bin/env python3
"""
Streamlit Cloud startup script
"""
import os
import sys
import streamlit as st

# Set up the environment
os.environ['PYTHONPATH'] = os.path.dirname(os.path.abspath(__file__))

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Run the main app
if __name__ == "__main__":
    # Import and run the app
    exec(open("app.py").read())
