import smtplib
import ssl
import os
from typing import Tuple

class EmailService:
    def __init__(self):
        self.gmail_email = os.environ.get("GMAIL_EMAIL") or ""
        self.gmail_password = os.environ.get("GMAIL_APP_PASSWORD") or ""
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
    
    def is_configured(self) -> bool:
        """Check if email service is properly configured"""
        return bool(self.gmail_email and self.gmail_password)
    
    def send_reset_email(self, to_email: str, reset_token: str, username: str) -> Tuple[bool, str]:
        """Send password reset email"""
        if not self.is_configured() or not self.gmail_email or not self.gmail_password:
            return False, "Email service not configured"
        
        try:
            # Create email message with proper headers
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            
            msg = MIMEMultipart()
            msg['From'] = self.gmail_email
            msg['To'] = to_email
            msg['Subject'] = "Stock Analysis Tool - Password Reset"
            
            body = f"""Hi {username},

You requested a password reset for your Stock Analysis Tool account.

Your password reset token is: {reset_token}

This token will expire in 1 hour. Please use it to reset your password.

If you didn't request this reset, please ignore this email.

Best regards,
Stock Analysis Tool Team
"""
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email with better error handling
            context = ssl.create_default_context()
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.gmail_email, self.gmail_password)
                server.sendmail(self.gmail_email, to_email, msg.as_string())
            
            return True, "Email sent successfully"
            
        except smtplib.SMTPAuthenticationError as e:
            return False, f"Gmail authentication failed: {str(e)}. Please verify your email and app password are correct."
        except smtplib.SMTPException as e:
            return False, f"SMTP error: {str(e)}"
        except Exception as e:
            return False, f"Unexpected error: {str(e)}"
    
    def send_welcome_email(self, to_email: str, username: str) -> Tuple[bool, str]:
        """Send welcome email to new users"""
        if not self.is_configured() or not self.gmail_email or not self.gmail_password:
            return False, "Email service not configured"
        
        try:
            # Create email message with proper headers
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            
            msg = MIMEMultipart()
            msg['From'] = self.gmail_email
            msg['To'] = to_email
            msg['Subject'] = "Welcome to Stock Analysis Tool!"
            
            body = f"""Welcome to Stock Analysis Tool, {username}!

Your account has been successfully created. You can now:

• Analyze stock data from Yahoo Finance
• Create price predictions using machine learning
• Save your favorite stocks
• View your analysis history
• Export data as CSV files

Start analyzing stocks by logging in to your account.

Happy investing!
Stock Analysis Tool Team
"""
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email with better error handling
            context = ssl.create_default_context()
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.gmail_email, self.gmail_password)
                server.sendmail(self.gmail_email, to_email, msg.as_string())
            
            return True, "Welcome email sent successfully"
            
        except smtplib.SMTPAuthenticationError as e:
            return False, f"Gmail authentication failed: {str(e)}. Please verify your email and app password are correct."
        except smtplib.SMTPException as e:
            return False, f"SMTP error: {str(e)}"
        except Exception as e:
            return False, f"Failed to send welcome email: {str(e)}"