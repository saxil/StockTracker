import logging
import yfinance as yf
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timezone # Added timezone
from ..models.database import Database # Adjusted Database import for consistency
from ..services.email_service import EmailService


class AlertSystem:
    """Stock price alert management system."""
    
    def __init__(self, db: Optional[Database] = None): # Removed email_service from constructor args
        """Initialize alert system."""
        self.db = db or Database()
        self.logger = logging.getLogger(__name__)
        # EmailService will be instantiated on demand in check_alerts

    def create_alert(self, username: str, symbol: str, alert_type: str,
                    threshold_value: float) -> Tuple[bool, str]:
        """Create a new price alert."""
        user = self.db.get_user(username)
        if not user:
            return False, "User not found."
        user_id = user['id'] # Get user_id

        valid_types = ['price_above', 'price_below', 'percent_change']
        if alert_type not in valid_types:
            return False, f"Invalid alert type. Must be one of: {valid_types}"
        
        if threshold_value <= 0 and alert_type != 'percent_change': # Percent change can be negative if we consider direction
             if alert_type == 'percent_change' and threshold_value == 0 :
                 pass # Allow 0% change if that's ever a use case, though UI implies positive
             elif threshold_value <=0 : # price_above/below must be positive
                return False, "Threshold value must be positive for price alerts."
        
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            # Check if 'regularMarketPrice' exists and is not None
            if not info or info.get('regularMarketPrice') is None:
                self.logger.warning(f"Potentially invalid stock symbol or no market price: {symbol}")
                # Allow creation, but it might not trigger if price is always None
                # return False, f"Invalid stock symbol or no market data: {symbol}"
        except Exception as e:
            self.logger.error(f"Error validating symbol {symbol} with yfinance: {e}")
            return False, f"Error validating symbol: {str(e)}"
        
        # Use user_id instead of username string in add_alert
        success = self.db.add_alert(user_id, symbol, alert_type, threshold_value, status='active')
        if success:
            return True, f"Alert created successfully for {symbol}"
        else:
            return False, "Failed to create alert in database"

    def get_user_alerts(self, username: str, status: Optional[str] = "active") -> List[Dict]:
        """Get alerts for a user, optionally filtered by status."""
        user = self.db.get_user(username)
        if not user:
            self.logger.warning(f"User {username} not found when trying to fetch alerts.")
            return []
        user_id = user['id']
        return self.db.get_alerts(user_id=user_id, status=status)

    def delete_alert(self, alert_id: int, username: str) -> bool: # Added username for ownership check
        """Deletes an alert by its ID, ensuring user ownership."""
        alert = self.db.get_alert_by_id(alert_id)
        user = self.db.get_user(username)
        if not alert or not user:
            self.logger.warning(f"Alert {alert_id} or user {username} not found for deletion.")
            return False
        if alert['user_id'] != user['id']:
            self.logger.warning(f"User {username} attempted to delete alert {alert_id} owned by another user.")
            return False
        return self.db.delete_alert_by_id(alert_id)

    def check_alerts(self) -> list[dict[str, any]]:
        """
        Checks all active alerts, triggers them if conditions are met,
        and sends email notifications.
        """
        newly_triggered_alerts: list[dict[str, any]] = []
        active_db_alerts = self.db.get_alerts(status="active") # Fetches all active alerts

        self.logger.info(f"Found {len(active_db_alerts)} active alerts to check.")

        for alert_dict in active_db_alerts:
            self.logger.info(f"Checking alert ID {alert_dict['id']} for stock {alert_dict['symbol']} (User ID: {alert_dict['user_id']})")
            try:
                ticker = yf.Ticker(alert_dict['symbol'])
                # Fetch last 2 days to ensure we have previous close for percent_change
                hist_data = ticker.history(period="2d", interval="1d")

                if hist_data.empty or 'Close' not in hist_data.columns:
                    self.logger.warning(f"No historical data or 'Close' column for {alert_dict['symbol']}. Skipping alert ID {alert_dict['id']}.")
                    continue
                
                if len(hist_data) == 0: # Should be caught by .empty but as a safeguard
                    self.logger.warning(f"Historical data for {alert_dict['symbol']} is empty after fetch. Skipping alert ID {alert_dict['id']}.")
                    continue

                current_price = hist_data['Close'].iloc[-1]

                triggered = False
                alert_type = alert_dict['alert_type']
                threshold = alert_dict['threshold_value']

                if alert_type == "price_above":
                    if current_price > threshold:
                        triggered = True
                elif alert_type == "price_below":
                    if current_price < threshold:
                        triggered = True
                elif alert_type == "percent_change":
                    if len(hist_data) < 2:
                        self.logger.warning(f"Not enough data for percent change calculation for {alert_dict['symbol']} (Alert ID: {alert_dict['id']}). Need 2 days, got {len(hist_data)}.")
                        continue

                    previous_price = hist_data['Close'].iloc[0] # First day is previous, last day is current
                    if previous_price == 0:
                        self.logger.warning(f"Previous price is 0 for {alert_dict['symbol']}. Skipping percent change for alert ID {alert_dict['id']}.")
                        continue
                    
                    percent_diff = ((current_price - previous_price) / previous_price) * 100
                    # For percent_change, threshold is typically positive (e.g., alert if changes by X%)
                    # The direction (positive or negative) is captured by abs(percent_diff)
                    if abs(percent_diff) >= threshold:
                        triggered = True

                if triggered:
                    self.logger.info(f"Alert ID {alert_dict['id']} for {alert_dict['symbol']} TRIGGERED at current price {current_price:.2f}")

                    # Update alert status in DB
                    update_success = self.db.update_alert(
                        alert_dict['id'],
                        {'status': 'triggered', 'triggered_at': datetime.now(timezone.utc).isoformat()}
                    )
                    if not update_success:
                        self.logger.error(f"Failed to update status for triggered alert ID {alert_dict['id']} in database.")
                        # Continue with notification attempt anyway, but log this failure

                    user_data = self.db.get_user_by_id(alert_dict['user_id'])

                    if user_data and user_data.get('email'):
                        recipient_email = user_data['email']
                        username_for_greeting = user_data.get('username', 'Valued User') # Fallback username

                        email_service = EmailService() # Instantiate per alert to get fresh config (if it ever changes)
                        if email_service.is_configured:
                            subject = f"Stock Alert Triggered: {alert_dict['symbol']}"
                            body = (
                                f"Hello {username_for_greeting},<br><br>"
                                f"Your alert for {alert_dict['symbol']} has been triggered.<br>"
                                f"<b>Alert Type:</b> {alert_type.replace('_', ' ').title()}<br>"
                                f"<b>Threshold:</b> {threshold}{'%' if alert_type == 'percent_change' else '$'}<br>"
                                f"<b>Current Price:</b> {float(current_price):.2f}<br><br>"
                                "Please log in to Stock Tracker for more details."
                            )
                            
                            email_sent = email_service.send_email(recipient_email, subject, body, body_type='html')
                            if email_sent:
                                self.logger.info(f"Email notification sent for alert ID {alert_dict['id']} to {recipient_email}")
                            else:
                                self.logger.warning(f"Failed to send email notification for alert ID {alert_dict['id']} to {recipient_email}")
                        else:
                            self.logger.info(f"Email service not configured. Skipping email for alert ID {alert_dict['id']}.")
                    else:
                        self.logger.warning(f"User email not found for user ID {alert_dict['user_id']} on alert ID {alert_dict['id']}. Cannot send email.")

                    # Add a copy of the original alert dict, or a new dict with relevant info
                    alert_info_for_return = alert_dict.copy()
                    alert_info_for_return['current_price_at_trigger'] = float(current_price)
                    alert_info_for_return['triggered_at_check_time'] = datetime.now(timezone.utc).isoformat()
                    newly_triggered_alerts.append(alert_info_for_return)

            except Exception as e:
                self.logger.error(f"Error checking alert ID {alert_dict.get('id', 'N/A')} for symbol {alert_dict.get('symbol', 'N/A')}: {e}", exc_info=True)
        
        self.logger.info(f"Finished checking alerts. {len(newly_triggered_alerts)} alerts were newly triggered.")
        return newly_triggered_alerts

    # Methods like _get_stock_prices, _should_trigger_alert, _trigger_alert, _send_alert_email, _get_user_email
    # are now effectively integrated into check_alerts or made redundant by the new direct approach.
    # They can be removed if not used elsewhere. For now, they are left but unused by the new check_alerts.

    def get_alert_history(self, username: str, limit: int = 50) -> List[Dict]:
        """Get triggered alerts history for a user."""
        user = self.db.get_user(username)
        if not user:
            self.logger.warning(f"User {username} not found when trying to fetch alert history.")
            return []
        user_id = user['id']
        return self.db.get_alerts(user_id=user_id, status='triggered', order_by='triggered_at DESC', limit=limit)
    
    def get_alert_statistics(self, username: str) -> Dict[str, any]: # Changed type hint
        """Get alert statistics for a user."""
        user = self.db.get_user(username)
        if not user:
            self.logger.warning(f"User {username} not found when trying to fetch alert stats.")
            return {'active_alerts': 0, 'triggered_alerts': 0, 'total_alerts': 0, 'by_type': {}}
        user_id = user['id']

        active_count = self.db.count_alerts(user_id=user_id, status='active')
        triggered_count = self.db.count_alerts(user_id=user_id, status='triggered')

        # For by_type, we might need a more specific DB method or iterate active/triggered
        # This is a simplified version. A more accurate by_type might query distinct types.
        all_user_alerts = self.db.get_alerts(user_id=user_id, status=None) # Get all alerts
        type_counts: Dict[str, int] = {}
        for alert in all_user_alerts:
            type_counts[alert['alert_type']] = type_counts.get(alert['alert_type'], 0) + 1

        return {
            'active_alerts': active_count,
            'triggered_alerts': triggered_count,
            'total_alerts': active_count + triggered_count, # Or count_alerts(user_id=user_id, status=None)
            'by_type': type_counts
        }

```
