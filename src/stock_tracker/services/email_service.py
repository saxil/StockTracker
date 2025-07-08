"""Email service for sending alerts and notifications."""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional
import logging


class EmailService:
    """Email service for sending stock alerts and notifications."""
    
    def __init__(self, smtp_server: str = "smtp.gmail.com", smtp_port: int = 587,
                 username: str = None, password: str = None):
        """Initialize email service."""
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.logger = logging.getLogger(__name__)
    
    def is_configured(self) -> bool:
        """Check if email service is properly configured."""
        return self.username is not None and self.password is not None
    
    def send_alert(self, to_email: str, subject: str, message: str) -> bool:
        """Send an email alert."""
        try:
            if not self.username or not self.password:
                self.logger.warning("Email credentials not configured")
                return False
            
            msg = MIMEMultipart()
            msg['From'] = self.username
            msg['To'] = to_email
            msg['Subject'] = subject
            
            msg.attach(MIMEText(message, 'plain'))
            
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.username, self.password)
            server.send_message(msg)
            server.quit()
            
            self.logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send email: {e}")
            return False
    
    def send_portfolio_update(self, to_email: str, portfolio_data: dict) -> bool:
        """Send portfolio update email."""
        subject = "Stock Portfolio Update"
        message = f"""
        Portfolio Update:
        
        Total Value: ${portfolio_data.get('total_value', 0):.2f}
        Daily Change: {portfolio_data.get('daily_change', 0):.2f}%
        
        Top Holdings:
        {portfolio_data.get('top_holdings', 'No holdings')}
        
        This is an automated message from your Stock Tracker.
        """
        
        return self.send_alert(to_email, subject, message)
    
    def send_price_alert(self, to_email: str, symbol: str, current_price: float,
                        alert_type: str, threshold: float) -> bool:
        """Send price alert email."""
        subject = f"Price Alert: {symbol}"
        message = f"""
        Price Alert Triggered!
        
        Stock: {symbol}
        Current Price: ${current_price:.2f}
        Alert Type: {alert_type}
        Threshold: ${threshold:.2f}
        
        This is an automated message from your Stock Tracker.
        """
        
        return self.send_alert(to_email, subject, message)
    
    def send_welcome_email(self, to_email: str, username: str) -> tuple[bool, str]:
        """Send welcome email to new user."""
        subject = "Welcome to Stock Tracker!"
        message = f"""
        Welcome to Stock Tracker, {username}!
        
        Your account has been successfully created. You can now:
        - Track your favorite stocks
        - Set up price alerts
        - Manage your portfolio
        - Perform technical analysis
        
        Get started by adding some stocks to your watchlist!
        
        Best regards,
        Stock Tracker Team
        """
        
        success = self.send_alert(to_email, subject, message)
        return success, "Welcome email sent successfully" if success else "Failed to send welcome email"
    
    def send_reset_email(self, to_email: str, token: str, username: str) -> tuple[bool, str]:
        """Send password reset email."""
        subject = "Password Reset Request - Stock Tracker"
        message = f"""
        Hi {username},
        
        You requested a password reset for your Stock Tracker account.
        
        Your reset token is: {token}
        
        Please use this token to reset your password. This token will expire in 24 hours.
        
        If you didn't request this reset, please ignore this email.
        
        Best regards,
        Stock Tracker Team
        """
        
        success = self.send_alert(to_email, subject, message)
        return success, "Reset email sent successfully" if success else "Failed to send reset email"
