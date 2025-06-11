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
    
    def get_configuration_status(self) -> dict:
        """Get detailed configuration status for debugging"""
        return {
            "email_configured": bool(self.gmail_email),
            "password_configured": bool(self.gmail_password),
            "is_fully_configured": self.is_configured(),
            "email_address": self.gmail_email if self.gmail_email else "Not set",
            "password_length": len(self.gmail_password) if self.gmail_password else 0
        }
    
    def test_connection(self) -> Tuple[bool, str]:
        """Test SMTP connection without sending email"""
        if not self.is_configured():
            return False, "Email service not configured - missing GMAIL_EMAIL or GMAIL_APP_PASSWORD environment variables"
        
        try:
            print("Testing SMTP connection...")
            context = ssl.create_default_context()
            with smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=30) as server:
                print("Starting TLS...")
                server.starttls(context=context)
                print("Attempting login...")
                server.login(self.gmail_email, self.gmail_password)
                print("Login successful!")
            return True, "SMTP connection successful"
        except smtplib.SMTPAuthenticationError as e:
            return False, f"Authentication failed: {str(e)}. Check your email and app password."
        except smtplib.SMTPServerDisconnected as e:
            return False, f"Server disconnected: {str(e)}. This could be due to network issues or firewall blocking SMTP."
        except Exception as e:
            return False, f"Connection error: {str(e)}"
    
    def send_reset_email(self, to_email: str, reset_token: str, username: str) -> Tuple[bool, str]:
        """Send password reset email"""
        if not self.is_configured():
            status = self.get_configuration_status()
            missing = []
            if not status["email_configured"]:
                missing.append("GMAIL_EMAIL")
            if not status["password_configured"]:
                missing.append("GMAIL_APP_PASSWORD")
            
            return False, f"Email service not configured. Missing environment variables: {', '.join(missing)}"
        
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
            with smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=30) as server:
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
        if not self.is_configured():
            # Don't fail account creation if email is not configured
            return False, "Email service not configured - welcome email skipped"
        
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
            with smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=30) as server:
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