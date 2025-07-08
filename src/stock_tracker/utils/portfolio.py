"""Portfolio management functionality."""

from typing import Dict, List, Tuple, Optional
from datetime import datetime, date
import pandas as pd
import yfinance as yf
from ..models.database import Database


class Portfolio:
    """Portfolio management class."""
    
    def __init__(self, username: str, db: Database = None):
        """Initialize portfolio for a user."""
        self.username = username
        self.db = db or Database()
    
    def add_holding(self, symbol: str, shares: float, purchase_price: float,
                   purchase_date: str = None) -> bool:
        """Add a stock holding to the portfolio."""
        if purchase_date is None:
            purchase_date = date.today().isoformat()
        
        return self.db.add_portfolio_holding(
            username=self.username,
            symbol=symbol.upper(),
            shares=shares,
            purchase_price=purchase_price,
            purchase_date=purchase_date
        )
    
    def get_holdings(self) -> List[Dict]:
        """Get all portfolio holdings."""
        return self.db.get_portfolio(self.username)
    
    def calculate_portfolio_value(self) -> Dict[str, float]:
        """Calculate current portfolio value and performance."""
        holdings = self.get_holdings()
        if not holdings:
            return {
                'total_value': 0.0,
                'total_cost': 0.0,
                'total_gain_loss': 0.0,
                'total_gain_loss_percent': 0.0
            }
        
        total_value = 0.0
        total_cost = 0.0
        
        # Get current prices for all symbols
        unique_symbols = list(set([holding['symbol'] for holding in holdings]))
        current_prices = self._get_current_prices(unique_symbols)
        
        for holding in holdings:
            symbol = holding['symbol']
            shares = holding['shares']
            purchase_price = holding['purchase_price']
            
            cost = shares * purchase_price
            current_price = current_prices.get(symbol, purchase_price)
            value = shares * current_price
            
            total_cost += cost
            total_value += value
        
        total_gain_loss = total_value - total_cost
        total_gain_loss_percent = (total_gain_loss / total_cost * 100) if total_cost > 0 else 0.0
        
        return {
            'total_value': total_value,
            'total_cost': total_cost,
            'total_gain_loss': total_gain_loss,
            'total_gain_loss_percent': total_gain_loss_percent
        }
    
    def get_detailed_holdings(self) -> List[Dict]:
        """Get detailed holdings with current prices and performance."""
        holdings = self.get_holdings()
        if not holdings:
            return []
        
        # Get current prices
        unique_symbols = list(set([holding['symbol'] for holding in holdings]))
        current_prices = self._get_current_prices(unique_symbols)
        
        detailed_holdings = []
        
        for holding in holdings:
            symbol = holding['symbol']
            shares = holding['shares']
            purchase_price = holding['purchase_price']
            purchase_date = holding['purchase_date']
            
            current_price = current_prices.get(symbol, purchase_price)
            cost = shares * purchase_price
            value = shares * current_price
            gain_loss = value - cost
            gain_loss_percent = (gain_loss / cost * 100) if cost > 0 else 0.0
            
            detailed_holding = {
                'symbol': symbol,
                'stock_name': holding.get('stock_name', symbol),
                'shares': shares,
                'purchase_price': purchase_price,
                'current_price': current_price,
                'purchase_date': purchase_date,
                'cost': cost,
                'value': value,
                'gain_loss': gain_loss,
                'gain_loss_percent': gain_loss_percent
            }
            
            detailed_holdings.append(detailed_holding)
        
        return detailed_holdings
    
    def get_portfolio_allocation(self) -> Dict[str, float]:
        """Get portfolio allocation by stock (percentage of total value)."""
        detailed_holdings = self.get_detailed_holdings()
        if not detailed_holdings:
            return {}
        
        total_value = sum(holding['value'] for holding in detailed_holdings)
        if total_value == 0:
            return {}
        
        allocation = {}
        for holding in detailed_holdings:
            symbol = holding['symbol']
            allocation_percent = (holding['value'] / total_value) * 100
            allocation[symbol] = allocation_percent
        
        return allocation
    
    def get_performance_summary(self) -> Dict[str, any]:
        """Get comprehensive portfolio performance summary."""
        portfolio_value = self.calculate_portfolio_value()
        detailed_holdings = self.get_detailed_holdings()
        allocation = self.get_portfolio_allocation()
        
        # Calculate additional metrics
        best_performer = None
        worst_performer = None
        
        if detailed_holdings:
            best_performer = max(detailed_holdings, key=lambda x: x['gain_loss_percent'])
            worst_performer = min(detailed_holdings, key=lambda x: x['gain_loss_percent'])
        
        return {
            'portfolio_value': portfolio_value,
            'holdings_count': len(detailed_holdings),
            'allocation': allocation,
            'best_performer': best_performer,
            'worst_performer': worst_performer,
            'last_updated': datetime.now().isoformat()
        }
    
    def _get_current_prices(self, symbols: List[str]) -> Dict[str, float]:
        """Get current prices for a list of symbols."""
        current_prices = {}
        
        for symbol in symbols:
            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period="1d")
                if not hist.empty:
                    current_prices[symbol] = hist['Close'].iloc[-1]
                else:
                    current_prices[symbol] = 0.0
            except Exception as e:
                print(f"Error getting price for {symbol}: {e}")
                current_prices[symbol] = 0.0
        
        return current_prices
    
    def get_dividend_summary(self) -> Dict[str, any]:
        """Get dividend information for portfolio holdings."""
        holdings = self.get_holdings()
        if not holdings:
            return {}
        
        unique_symbols = list(set([holding['symbol'] for holding in holdings]))
        dividend_data = {}
        total_annual_dividends = 0.0
        
        for symbol in unique_symbols:
            try:
                ticker = yf.Ticker(symbol)
                info = ticker.info
                dividends = ticker.dividends
                
                dividend_yield = info.get('dividendYield', 0) or 0
                dividend_rate = info.get('dividendRate', 0) or 0
                
                # Calculate total shares for this symbol
                total_shares = sum(h['shares'] for h in holdings if h['symbol'] == symbol)
                annual_dividend_income = total_shares * dividend_rate
                total_annual_dividends += annual_dividend_income
                
                dividend_data[symbol] = {
                    'dividend_yield': dividend_yield * 100,  # Convert to percentage
                    'dividend_rate': dividend_rate,
                    'total_shares': total_shares,
                    'annual_income': annual_dividend_income,
                    'last_dividend_date': dividends.index[-1].strftime('%Y-%m-%d') if not dividends.empty else None
                }
                
            except Exception as e:
                print(f"Error getting dividend data for {symbol}: {e}")
                dividend_data[symbol] = {
                    'dividend_yield': 0,
                    'dividend_rate': 0,
                    'total_shares': 0,
                    'annual_income': 0,
                    'last_dividend_date': None
                }
        
        return {
            'stocks': dividend_data,
            'total_annual_dividends': total_annual_dividends,
            'average_yield': sum(d['dividend_yield'] for d in dividend_data.values()) / len(dividend_data) if dividend_data else 0
        }
    
    def export_to_csv(self) -> str:
        """Export portfolio holdings to CSV format."""
        detailed_holdings = self.get_detailed_holdings()
        if not detailed_holdings:
            return ""
        
        df = pd.DataFrame(detailed_holdings)
        return df.to_csv(index=False)
    
    def get_portfolio_history(self, days: int = 30) -> Dict[str, any]:
        """Get portfolio performance history over specified days."""
        # This would require historical portfolio data tracking
        # For now, return current performance
        return self.get_performance_summary()
    
    def rebalance_suggestions(self, target_allocation: Dict[str, float] = None) -> List[Dict]:
        """Suggest portfolio rebalancing based on target allocation."""
        current_allocation = self.get_portfolio_allocation()
        if not current_allocation:
            return []
        
        # If no target allocation provided, suggest equal weighting
        if target_allocation is None:
            num_stocks = len(current_allocation)
            target_allocation = {symbol: 100/num_stocks for symbol in current_allocation.keys()}
        
        suggestions = []
        for symbol, target_percent in target_allocation.items():
            current_percent = current_allocation.get(symbol, 0)
            difference = target_percent - current_percent
            
            if abs(difference) > 1:  # Only suggest if difference > 1%
                action = "BUY" if difference > 0 else "SELL"
                suggestions.append({
                    'symbol': symbol,
                    'action': action,
                    'current_allocation': current_percent,
                    'target_allocation': target_percent,
                    'difference': difference
                })
        
        return sorted(suggestions, key=lambda x: abs(x['difference']), reverse=True)
