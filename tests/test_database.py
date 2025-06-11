"""Unit tests for the database module."""

import unittest
import tempfile
import os
from datetime import date, datetime
from src.stock_tracker.models.database import Database


class TestDatabase(unittest.TestCase):
    """Test cases for Database class."""
    
    def setUp(self):
        """Set up test database."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test.db")
        self.db = Database(self.db_path)
    
    def tearDown(self):
        """Clean up test database."""
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        os.rmdir(self.temp_dir)
    
    def test_database_initialization(self):
        """Test database initialization."""
        self.assertTrue(os.path.exists(self.db_path))
        
        # Check if tables are created
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            expected_tables = ['stocks', 'stock_data', 'portfolio', 'alerts', 'analysis_history']
            for table in expected_tables:
                self.assertIn(table, tables)
    
    def test_add_stock(self):
        """Test adding a stock."""
        success = self.db.add_stock("AAPL", "Apple Inc.", "NASDAQ", "Technology", "Consumer Electronics")
        self.assertTrue(success)
        
        # Verify stock was added
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM stocks WHERE symbol = ?", ("AAPL",))
            stock = cursor.fetchone()
            
            self.assertIsNotNone(stock)
            self.assertEqual(stock['symbol'], "AAPL")
            self.assertEqual(stock['name'], "Apple Inc.")
            self.assertEqual(stock['exchange'], "NASDAQ")
    
    def test_add_stock_data(self):
        """Test adding stock price data."""
        # First add the stock
        self.db.add_stock("AAPL", "Apple Inc.")
        
        # Add stock data
        success = self.db.add_stock_data(
            "AAPL", "2023-01-01", 100.0, 105.0, 99.0, 104.0, 103.5, 1000000
        )
        self.assertTrue(success)
        
        # Verify data was added
        data = self.db.get_stock_data("AAPL")
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['symbol'], "AAPL")
        self.assertEqual(data[0]['close_price'], 104.0)
    
    def test_portfolio_operations(self):
        """Test portfolio operations."""
        # Add stock first
        self.db.add_stock("AAPL", "Apple Inc.")
        
        # Add portfolio holding
        success = self.db.add_portfolio_holding("testuser", "AAPL", 10.0, 150.0, "2023-01-01")
        self.assertTrue(success)
        
        # Get portfolio
        portfolio = self.db.get_portfolio("testuser")
        self.assertEqual(len(portfolio), 1)
        self.assertEqual(portfolio[0]['symbol'], "AAPL")
        self.assertEqual(portfolio[0]['shares'], 10.0)
    
    def test_alert_operations(self):
        """Test alert operations."""
        # Add stock first
        self.db.add_stock("AAPL", "Apple Inc.")
        
        # Add alert
        success = self.db.add_alert("testuser", "AAPL", "price_above", 200.0)
        self.assertTrue(success)
        
        # Get active alerts
        alerts = self.db.get_active_alerts("testuser")
        self.assertEqual(len(alerts), 1)
        self.assertEqual(alerts[0]['symbol'], "AAPL")
        self.assertEqual(alerts[0]['threshold_value'], 200.0)
        
        # Trigger alert
        alert_id = alerts[0]['id']
        success = self.db.trigger_alert(alert_id)
        self.assertTrue(success)
        
        # Verify alert is no longer active
        active_alerts = self.db.get_active_alerts("testuser")
        self.assertEqual(len(active_alerts), 0)
    
    def test_analysis_history(self):
        """Test analysis history operations."""
        # Save analysis
        success = self.db.save_analysis("testuser", "AAPL", "technical_analysis", 
                                       "RSI=14", "RSI=65.5")
        self.assertTrue(success)
        
        # Get analysis history
        history = self.db.get_analysis_history("testuser")
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]['symbol'], "AAPL")
        self.assertEqual(history[0]['analysis_type'], "technical_analysis")


if __name__ == '__main__':
    unittest.main()
