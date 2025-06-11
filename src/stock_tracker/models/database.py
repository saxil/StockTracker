"""Database models and management for stock tracking."""

import sqlite3
import os
from datetime import datetime
from typing import List, Optional, Dict, Any
from contextlib import contextmanager


class Database:
    """Database manager for stock tracker."""
    
    def __init__(self, db_path: str = "data/stocks.db"):
        """Initialize database connection."""
        self.db_path = db_path
        self.ensure_db_dir()
        self.init_database()
    
    def ensure_db_dir(self):
        """Ensure database directory exists."""
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
    
    @contextmanager
    def get_connection(self):
        """Get database connection with context manager."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def init_database(self):
        """Initialize database tables."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Stocks table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS stocks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT UNIQUE NOT NULL,
                    name TEXT NOT NULL,
                    exchange TEXT,
                    sector TEXT,
                    industry TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Stock data table for historical prices
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS stock_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    date DATE NOT NULL,
                    open_price REAL NOT NULL,
                    high_price REAL NOT NULL,
                    low_price REAL NOT NULL,
                    close_price REAL NOT NULL,
                    adj_close_price REAL NOT NULL,
                    volume INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (symbol) REFERENCES stocks (symbol),
                    UNIQUE(symbol, date)
                )
            """)
            
            # Portfolio table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS portfolio (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    symbol TEXT NOT NULL,
                    shares REAL NOT NULL,
                    purchase_price REAL NOT NULL,
                    purchase_date DATE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (symbol) REFERENCES stocks (symbol)
                )
            """)
            
            # Alerts table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    symbol TEXT NOT NULL,
                    alert_type TEXT NOT NULL CHECK (alert_type IN ('price_above', 'price_below', 'percent_change')),
                    threshold_value REAL NOT NULL,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    triggered_at TIMESTAMP NULL,
                    FOREIGN KEY (symbol) REFERENCES stocks (symbol)
                )
            """)
            
            # Analysis history table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS analysis_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    symbol TEXT NOT NULL,
                    analysis_type TEXT NOT NULL,
                    parameters TEXT,
                    results TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
    
    def add_stock(self, symbol: str, name: str, exchange: str = None, 
                  sector: str = None, industry: str = None) -> bool:
        """Add a new stock to the database."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO stocks (symbol, name, exchange, sector, industry, updated_at)
                    VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                """, (symbol.upper(), name, exchange, sector, industry))
                conn.commit()
                return True
        except Exception as e:
            print(f"Error adding stock {symbol}: {e}")
            return False
    
    def add_stock_data(self, symbol: str, date: str, open_price: float, 
                       high_price: float, low_price: float, close_price: float,
                       adj_close_price: float, volume: int) -> bool:
        """Add stock price data to the database."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO stock_data 
                    (symbol, date, open_price, high_price, low_price, close_price, adj_close_price, volume)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (symbol.upper(), date, open_price, high_price, low_price, 
                     close_price, adj_close_price, volume))
                conn.commit()
                return True
        except Exception as e:
            print(f"Error adding stock data for {symbol}: {e}")
            return False
    
    def get_stock_data(self, symbol: str, start_date: str = None, 
                       end_date: str = None) -> List[Dict[str, Any]]:
        """Get historical stock data."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                query = "SELECT * FROM stock_data WHERE symbol = ?"
                params = [symbol.upper()]
                
                if start_date:
                    query += " AND date >= ?"
                    params.append(start_date)
                
                if end_date:
                    query += " AND date <= ?"
                    params.append(end_date)
                
                query += " ORDER BY date ASC"
                
                cursor.execute(query, params)
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"Error getting stock data for {symbol}: {e}")
            return []
    
    def add_portfolio_holding(self, username: str, symbol: str, shares: float,
                            purchase_price: float, purchase_date: str) -> bool:
        """Add a portfolio holding."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO portfolio (username, symbol, shares, purchase_price, purchase_date)
                    VALUES (?, ?, ?, ?, ?)
                """, (username, symbol.upper(), shares, purchase_price, purchase_date))
                conn.commit()
                return True
        except Exception as e:
            print(f"Error adding portfolio holding: {e}")
            return False
    
    def get_portfolio(self, username: str) -> List[Dict[str, Any]]:
        """Get user's portfolio holdings."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT p.*, s.name as stock_name
                    FROM portfolio p
                    LEFT JOIN stocks s ON p.symbol = s.symbol
                    WHERE p.username = ?
                    ORDER BY p.created_at DESC
                """, (username,))
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"Error getting portfolio for {username}: {e}")
            return []
    
    def add_alert(self, username: str, symbol: str, alert_type: str,
                  threshold_value: float) -> bool:
        """Add a price alert."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO alerts (username, symbol, alert_type, threshold_value)
                    VALUES (?, ?, ?, ?)
                """, (username, symbol.upper(), alert_type, threshold_value))
                conn.commit()
                return True
        except Exception as e:
            print(f"Error adding alert: {e}")
            return False
    
    def get_active_alerts(self, username: str = None) -> List[Dict[str, Any]]:
        """Get active alerts."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                query = "SELECT * FROM alerts WHERE is_active = 1"
                params = []
                
                if username:
                    query += " AND username = ?"
                    params.append(username)
                
                cursor.execute(query, params)
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"Error getting alerts: {e}")
            return []
    
    def trigger_alert(self, alert_id: int) -> bool:
        """Mark alert as triggered."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE alerts 
                    SET is_active = 0, triggered_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (alert_id,))
                conn.commit()
                return True
        except Exception as e:
            print(f"Error triggering alert {alert_id}: {e}")
            return False
    
    def save_analysis(self, username: str, symbol: str, analysis_type: str,
                     parameters: str = None, results: str = None) -> bool:
        """Save analysis results."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO analysis_history (username, symbol, analysis_type, parameters, results)
                    VALUES (?, ?, ?, ?, ?)
                """, (username, symbol.upper(), analysis_type, parameters, results))
                conn.commit()
                return True
        except Exception as e:
            print(f"Error saving analysis: {e}")
            return False
    
    def get_analysis_history(self, username: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get user's analysis history."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM analysis_history 
                    WHERE username = ?
                    ORDER BY created_at DESC
                    LIMIT ?
                """, (username, limit))
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"Error getting analysis history: {e}")
            return []
