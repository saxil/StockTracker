"""Unit tests for portfolio management module."""

import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import date
import pandas as pd
from src.stock_tracker.utils.portfolio import Portfolio
from src.stock_tracker.models.database import Database


class TestPortfolio(unittest.TestCase):
    """Test cases for Portfolio class."""
    
    def setUp(self):
        """Set up test portfolio."""
        self.mock_db = Mock(spec=Database)
        self.portfolio = Portfolio("testuser", self.mock_db)
    
    def test_add_holding(self):
        """Test adding a holding to portfolio."""
        self.mock_db.add_portfolio_holding.return_value = True
        
        result = self.portfolio.add_holding("AAPL", 10.0, 150.0, "2023-01-01")
        
        self.assertTrue(result)
        self.mock_db.add_portfolio_holding.assert_called_once_with(
            username="testuser",
            symbol="AAPL",
            shares=10.0,
            purchase_price=150.0,
            purchase_date="2023-01-01"
        )
    
    def test_add_holding_without_date(self):
        """Test adding a holding without specifying date."""
        self.mock_db.add_portfolio_holding.return_value = True
        
        with patch('src.stock_tracker.utils.portfolio.date') as mock_date:
            mock_date.today.return_value.isoformat.return_value = "2023-06-15"
            
            result = self.portfolio.add_holding("AAPL", 10.0, 150.0)
            
            self.assertTrue(result)
            self.mock_db.add_portfolio_holding.assert_called_once_with(
                username="testuser",
                symbol="AAPL",
                shares=10.0,
                purchase_price=150.0,
                purchase_date="2023-06-15"
            )
    
    def test_get_holdings(self):
        """Test getting portfolio holdings."""
        mock_holdings = [
            {
                'symbol': 'AAPL',
                'shares': 10.0,
                'purchase_price': 150.0,
                'purchase_date': '2023-01-01',
                'stock_name': 'Apple Inc.'
            }
        ]
        self.mock_db.get_portfolio.return_value = mock_holdings
        
        holdings = self.portfolio.get_holdings()
        
        self.assertEqual(holdings, mock_holdings)
        self.mock_db.get_portfolio.assert_called_once_with("testuser")
    
    @patch('src.stock_tracker.utils.portfolio.yf.Ticker')
    def test_calculate_portfolio_value(self, mock_ticker):
        """Test portfolio value calculation."""
        # Mock holdings
        mock_holdings = [
            {
                'symbol': 'AAPL',
                'shares': 10.0,
                'purchase_price': 150.0,
                'purchase_date': '2023-01-01'
            },
            {
                'symbol': 'GOOGL',
                'shares': 5.0,
                'purchase_price': 2000.0,
                'purchase_date': '2023-01-01'
            }
        ]
        self.mock_db.get_portfolio.return_value = mock_holdings
        
        # Mock stock prices
        mock_aapl_ticker = Mock()
        mock_aapl_hist = pd.DataFrame({'Close': [180.0]})  # Current price $180
        mock_aapl_ticker.history.return_value = mock_aapl_hist
        
        mock_googl_ticker = Mock()
        mock_googl_hist = pd.DataFrame({'Close': [2100.0]})  # Current price $2100
        mock_googl_ticker.history.return_value = mock_googl_hist
        
        def mock_ticker_side_effect(symbol):
            if symbol == 'AAPL':
                return mock_aapl_ticker
            elif symbol == 'GOOGL':
                return mock_googl_ticker
        
        mock_ticker.side_effect = mock_ticker_side_effect
        
        # Calculate portfolio value
        portfolio_value = self.portfolio.calculate_portfolio_value()
        
        # Expected calculations:
        # AAPL: 10 shares * $180 = $1800 (cost: 10 * $150 = $1500)
        # GOOGL: 5 shares * $2100 = $10500 (cost: 5 * $2000 = $10000)
        # Total value: $12300, Total cost: $11500, Gain: $800
        
        expected_total_value = 1800.0 + 10500.0
        expected_total_cost = 1500.0 + 10000.0
        expected_gain_loss = expected_total_value - expected_total_cost
        expected_gain_loss_percent = (expected_gain_loss / expected_total_cost) * 100
        
        self.assertAlmostEqual(portfolio_value['total_value'], expected_total_value, places=2)
        self.assertAlmostEqual(portfolio_value['total_cost'], expected_total_cost, places=2)
        self.assertAlmostEqual(portfolio_value['total_gain_loss'], expected_gain_loss, places=2)
        self.assertAlmostEqual(portfolio_value['total_gain_loss_percent'], expected_gain_loss_percent, places=2)
    
    def test_calculate_portfolio_value_empty(self):
        """Test portfolio value calculation with empty portfolio."""
        self.mock_db.get_portfolio.return_value = []
        
        portfolio_value = self.portfolio.calculate_portfolio_value()
        
        expected = {
            'total_value': 0.0,
            'total_cost': 0.0,
            'total_gain_loss': 0.0,
            'total_gain_loss_percent': 0.0
        }
        
        self.assertEqual(portfolio_value, expected)
    
    @patch('src.stock_tracker.utils.portfolio.yf.Ticker')
    def test_get_detailed_holdings(self, mock_ticker):
        """Test getting detailed holdings with performance metrics."""
        # Mock holdings
        mock_holdings = [
            {
                'symbol': 'AAPL',
                'shares': 10.0,
                'purchase_price': 150.0,
                'purchase_date': '2023-01-01',
                'stock_name': 'Apple Inc.'
            }
        ]
        self.mock_db.get_portfolio.return_value = mock_holdings
        
        # Mock current price
        mock_aapl_ticker = Mock()
        mock_aapl_hist = pd.DataFrame({'Close': [180.0]})
        mock_aapl_ticker.history.return_value = mock_aapl_hist
        mock_ticker.return_value = mock_aapl_ticker
        
        detailed_holdings = self.portfolio.get_detailed_holdings()
        
        self.assertEqual(len(detailed_holdings), 1)
        
        holding = detailed_holdings[0]
        self.assertEqual(holding['symbol'], 'AAPL')
        self.assertEqual(holding['shares'], 10.0)
        self.assertEqual(holding['purchase_price'], 150.0)
        self.assertEqual(holding['current_price'], 180.0)
        self.assertEqual(holding['cost'], 1500.0)  # 10 * 150
        self.assertEqual(holding['value'], 1800.0)  # 10 * 180
        self.assertEqual(holding['gain_loss'], 300.0)  # 1800 - 1500
        self.assertEqual(holding['gain_loss_percent'], 20.0)  # (300 / 1500) * 100
    
    @patch('src.stock_tracker.utils.portfolio.yf.Ticker')
    def test_get_portfolio_allocation(self, mock_ticker):
        """Test portfolio allocation calculation."""
        # Mock holdings with multiple stocks
        mock_holdings = [
            {'symbol': 'AAPL', 'shares': 10.0, 'purchase_price': 150.0, 'purchase_date': '2023-01-01'},
            {'symbol': 'GOOGL', 'shares': 5.0, 'purchase_price': 2000.0, 'purchase_date': '2023-01-01'}
        ]
        self.mock_db.get_portfolio.return_value = mock_holdings
        
        # Mock current prices
        def mock_ticker_side_effect(symbol):
            mock_ticker_obj = Mock()
            if symbol == 'AAPL':
                mock_ticker_obj.history.return_value = pd.DataFrame({'Close': [200.0]})  # $2000 value
            elif symbol == 'GOOGL':
                mock_ticker_obj.history.return_value = pd.DataFrame({'Close': [3000.0]})  # $15000 value
            return mock_ticker_obj
        
        mock_ticker.side_effect = mock_ticker_side_effect
        
        allocation = self.portfolio.get_portfolio_allocation()
        
        # Expected: AAPL $2000, GOOGL $15000, Total $17000
        # AAPL allocation: (2000/17000) * 100 = 11.76%
        # GOOGL allocation: (15000/17000) * 100 = 88.24%
        
        self.assertAlmostEqual(allocation['AAPL'], 11.76, places=1)
        self.assertAlmostEqual(allocation['GOOGL'], 88.24, places=1)
    
    def test_export_to_csv(self):
        """Test CSV export functionality."""
        with patch.object(self.portfolio, 'get_detailed_holdings') as mock_detailed:
            mock_detailed.return_value = [
                {
                    'symbol': 'AAPL',
                    'stock_name': 'Apple Inc.',
                    'shares': 10.0,
                    'purchase_price': 150.0,
                    'current_price': 180.0,
                    'cost': 1500.0,
                    'value': 1800.0,
                    'gain_loss': 300.0,
                    'gain_loss_percent': 20.0
                }
            ]
            
            csv_data = self.portfolio.export_to_csv()
            
            # Check that CSV contains expected data
            self.assertIn('AAPL', csv_data)
            self.assertIn('Apple Inc.', csv_data)
            self.assertIn('10.0', csv_data)
            self.assertIn('150.0', csv_data)
    
    def test_export_to_csv_empty(self):
        """Test CSV export with empty portfolio."""
        with patch.object(self.portfolio, 'get_detailed_holdings') as mock_detailed:
            mock_detailed.return_value = []
            
            csv_data = self.portfolio.export_to_csv()
            
            self.assertEqual(csv_data, "")
    
    def test_rebalance_suggestions(self):
        """Test portfolio rebalancing suggestions."""
        with patch.object(self.portfolio, 'get_portfolio_allocation') as mock_allocation:
            mock_allocation.return_value = {
                'AAPL': 60.0,  # Currently 60%
                'GOOGL': 40.0  # Currently 40%
            }
            
            # Suggest equal weighting (50% each)
            target_allocation = {'AAPL': 50.0, 'GOOGL': 50.0}
            suggestions = self.portfolio.rebalance_suggestions(target_allocation)
            
            # Should suggest selling AAPL (reduce from 60% to 50%)
            # and buying GOOGL (increase from 40% to 50%)
            self.assertEqual(len(suggestions), 2)
            
            aapl_suggestion = next(s for s in suggestions if s['symbol'] == 'AAPL')
            googl_suggestion = next(s for s in suggestions if s['symbol'] == 'GOOGL')
            
            self.assertEqual(aapl_suggestion['action'], 'SELL')
            self.assertEqual(aapl_suggestion['difference'], -10.0)
            
            self.assertEqual(googl_suggestion['action'], 'BUY')
            self.assertEqual(googl_suggestion['difference'], 10.0)


if __name__ == '__main__':
    unittest.main()
