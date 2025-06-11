"""Stock price alert system."""

import yfinance as yf
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from .database import Database
from ..services.email_service import EmailService


class AlertSystem:
    """Stock price alert management system."""
    
    def __init__(self, db: Database = None, email_service: EmailService = None):
        """Initialize alert system."""
        self.db = db or Database()
        self.email_service = email_service or EmailService()
    
    def create_alert(self, username: str, symbol: str, alert_type: str,
                    threshold_value: float) -> Tuple[bool, str]:
        """Create a new price alert."""
        valid_types = ['price_above', 'price_below', 'percent_change']
        
        if alert_type not in valid_types:
            return False, f"Invalid alert type. Must be one of: {valid_types}"
        
        if threshold_value <= 0:
            return False, "Threshold value must be positive"
        
        # Validate stock symbol
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            if not info or 'symbol' not in info:
                return False, f"Invalid stock symbol: {symbol}"
        except Exception as e:
            return False, f"Error validating symbol: {str(e)}"
        
        success = self.db.add_alert(username, symbol, alert_type, threshold_value)
        if success:
            return True, f"Alert created successfully for {symbol}"
        else:
            return False, "Failed to create alert"
    
    def get_user_alerts(self, username: str) -> List[Dict]:
        """Get all active alerts for a user."""
        return self.db.get_active_alerts(username)
    
    def delete_alert(self, alert_id: int) -> bool:
        """Delete an alert."""
        return self.db.trigger_alert(alert_id)  # This marks it as inactive
    
    def check_alerts(self) -> List[Dict]:
        """Check all active alerts and trigger notifications."""
        active_alerts = self.db.get_active_alerts()
        triggered_alerts = []
        
        if not active_alerts:
            return triggered_alerts
        
        # Group alerts by symbol to minimize API calls
        alerts_by_symbol = {}
        for alert in active_alerts:
            symbol = alert['symbol']
            if symbol not in alerts_by_symbol:
                alerts_by_symbol[symbol] = []
            alerts_by_symbol[symbol].append(alert)
        
        # Check each symbol's current price
        for symbol, symbol_alerts in alerts_by_symbol.items():
            try:
                current_price, previous_close = self._get_stock_prices(symbol)
                if current_price is None:
                    continue
                
                for alert in symbol_alerts:
                    should_trigger = self._should_trigger_alert(
                        alert, current_price, previous_close
                    )
                    
                    if should_trigger:
                        # Trigger the alert
                        success = self._trigger_alert(alert, current_price)
                        if success:
                            triggered_alerts.append({
                                'alert': alert,
                                'current_price': current_price,
                                'triggered_at': datetime.now()
                            })
                            
            except Exception as e:
                print(f"Error checking alerts for {symbol}: {e}")
                continue
        
        return triggered_alerts
    
    def _get_stock_prices(self, symbol: str) -> Tuple[Optional[float], Optional[float]]:
        """Get current and previous close prices for a symbol."""
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="2d")
            
            if len(hist) < 1:
                return None, None
            
            current_price = hist['Close'].iloc[-1]
            previous_close = hist['Close'].iloc[-2] if len(hist) > 1 else current_price
            
            return float(current_price), float(previous_close)
            
        except Exception as e:
            print(f"Error getting prices for {symbol}: {e}")
            return None, None
    
    def _should_trigger_alert(self, alert: Dict, current_price: float,
                            previous_close: float) -> bool:
        """Determine if an alert should be triggered."""
        alert_type = alert['alert_type']
        threshold = alert['threshold_value']
        
        if alert_type == 'price_above':
            return current_price >= threshold
        
        elif alert_type == 'price_below':
            return current_price <= threshold
        
        elif alert_type == 'percent_change':
            if previous_close == 0:
                return False
            
            percent_change = abs((current_price - previous_close) / previous_close * 100)
            return percent_change >= threshold
        
        return False
    
    def _trigger_alert(self, alert: Dict, current_price: float) -> bool:
        """Trigger an alert and send notification."""
        try:
            # Mark alert as triggered in database
            self.db.trigger_alert(alert['id'])
            
            # Send email notification if email service is configured
            if self.email_service.is_configured():
                self._send_alert_email(alert, current_price)
            
            return True
            
        except Exception as e:
            print(f"Error triggering alert {alert['id']}: {e}")
            return False
    
    def _send_alert_email(self, alert: Dict, current_price: float):
        """Send email notification for triggered alert."""
        try:
            username = alert['username']
            symbol = alert['symbol']
            alert_type = alert['alert_type']
            threshold = alert['threshold_value']
            
            # Get user's email (this would need to be implemented)
            user_email = self._get_user_email(username)  
            if not user_email:
                return
            
            subject = f"🚨 Stock Alert Triggered: {symbol}"
            
            if alert_type == 'price_above':
                message = f"""
                Your stock alert has been triggered!
                
                Stock: {symbol}
                Alert Type: Price Above Threshold
                Threshold: ${threshold:.2f}
                Current Price: ${current_price:.2f}
                
                The stock price has exceeded your target threshold.
                
                This is an automated alert from your Stock Tracker application.
                """
            
            elif alert_type == 'price_below':
                message = f"""
                Your stock alert has been triggered!
                
                Stock: {symbol}
                Alert Type: Price Below Threshold
                Threshold: ${threshold:.2f}
                Current Price: ${current_price:.2f}
                
                The stock price has fallen below your target threshold.
                
                This is an automated alert from your Stock Tracker application.
                """
            
            elif alert_type == 'percent_change':
                message = f"""
                Your stock alert has been triggered!
                
                Stock: {symbol}
                Alert Type: Significant Price Change
                Threshold: {threshold:.1f}%
                Current Price: ${current_price:.2f}
                
                The stock has experienced a significant price movement.
                
                This is an automated alert from your Stock Tracker application.
                """
            
            # Send the email
            self.email_service.send_alert_email(user_email, subject, message)
            
        except Exception as e:
            print(f"Error sending alert email: {e}")
    
    def _get_user_email(self, username: str) -> Optional[str]:
        """Get user's email address from user database."""
        # This would need to integrate with the user authentication system
        # For now, return None - this should be implemented based on your auth system
        return None
    
    def get_alert_history(self, username: str, limit: int = 50) -> List[Dict]:
        """Get triggered alerts history for a user."""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM alerts 
                    WHERE username = ? AND triggered_at IS NOT NULL
                    ORDER BY triggered_at DESC
                    LIMIT ?
                """, (username, limit))
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"Error getting alert history: {e}")
            return []
    
    def get_alert_statistics(self, username: str) -> Dict[str, int]:
        """Get alert statistics for a user."""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                
                # Count active alerts
                cursor.execute("SELECT COUNT(*) FROM alerts WHERE username = ? AND is_active = 1", (username,))
                active_count = cursor.fetchone()[0]
                
                # Count triggered alerts
                cursor.execute("SELECT COUNT(*) FROM alerts WHERE username = ? AND triggered_at IS NOT NULL", (username,))
                triggered_count = cursor.fetchone()[0]
                
                # Count by alert type
                cursor.execute("""
                    SELECT alert_type, COUNT(*) 
                    FROM alerts 
                    WHERE username = ? 
                    GROUP BY alert_type
                """, (username,))
                type_counts = {row[0]: row[1] for row in cursor.fetchall()}
                
                return {
                    'active_alerts': active_count,
                    'triggered_alerts': triggered_count,
                    'total_alerts': active_count + triggered_count,
                    'by_type': type_counts
                }
                
        except Exception as e:
            print(f"Error getting alert statistics: {e}")
            return {
                'active_alerts': 0,
                'triggered_alerts': 0,
                'total_alerts': 0,
                'by_type': {}
            }
