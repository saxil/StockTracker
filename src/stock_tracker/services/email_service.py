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
        """Test SMTP connection and verify email sending capability"""
        if not self.is_configured():
            return False, "Email service not configured - missing GMAIL_EMAIL or GMAIL_APP_PASSWORD environment variables"
        
        try:
            print("🔍 Testing SMTP connection and authentication...")
            context = ssl.create_default_context()
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=30) as server:
                print("🔒 Starting TLS encryption...")
                server.starttls(context=context)
                
                print("🔑 Attempting Gmail login...")
                server.login(self.gmail_email, self.gmail_password)
                
                print("✅ Login successful!")
                print("📧 SMTP connection and authentication verified!")
                
                # Test email composition (without sending)
                from email.mime.text import MIMEText
                from email.mime.multipart import MIMEMultipart
                
                test_msg = MIMEMultipart()
                test_msg['From'] = self.gmail_email
                test_msg['To'] = self.gmail_email  # Send to self for testing
                test_msg['Subject'] = "Test Email - Connection Verification"
                test_msg.attach(MIMEText("This is a test email to verify email functionality.", 'plain'))
                
                print("📝 Email composition test successful!")
                
            return True, "SMTP connection, authentication, and email composition all verified successfully"
            
        except smtplib.SMTPAuthenticationError as e:
            error_msg = f"Authentication failed: {str(e)}. Check your email and app password."
            print(f"❌ {error_msg}")
            return False, error_msg
        except smtplib.SMTPServerDisconnected as e:
            error_msg = f"Server disconnected: {str(e)}. This could be due to network issues or firewall blocking SMTP."
            print(f"❌ {error_msg}")
            return False, error_msg
        except Exception as e:
            error_msg = f"Connection error: {str(e)}"
            print(f"❌ {error_msg}")
            return False, error_msg
    
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
            
            # Send email with comprehensive error handling and verification
            print(f"📧 Attempting to send reset email to {to_email}...")
            context = ssl.create_default_context()
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=30) as server:
                print("🔒 Establishing secure connection...")
                server.starttls(context=context)
                
                print("🔑 Authenticating with Gmail...")
                server.login(self.gmail_email, self.gmail_password)
                
                print("📤 Sending email...")
                # sendmail returns a dictionary of failed recipients
                # Empty dict means all recipients succeeded
                failed_recipients = server.sendmail(self.gmail_email, [to_email], msg.as_string())
                
                if failed_recipients:
                    # Some recipients failed
                    failed_emails = list(failed_recipients.keys())
                    return False, f"Failed to send email to: {', '.join(failed_emails)}"
                else:
                    # All recipients succeeded
                    print("✅ Email sent successfully!")
                    return True, f"Password reset email successfully sent to {to_email}"
            
        except smtplib.SMTPAuthenticationError as e:
            error_msg = f"Gmail authentication failed: {str(e)}. Please verify your email and app password are correct."
            print(f"❌ {error_msg}")
            return False, error_msg
        except smtplib.SMTPRecipientsRefused as e:
            error_msg = f"Email address '{to_email}' was rejected by the server: {str(e)}"
            print(f"❌ {error_msg}")
            return False, error_msg
        except smtplib.SMTPSenderRefused as e:
            error_msg = f"Sender email '{self.gmail_email}' was rejected: {str(e)}"
            print(f"❌ {error_msg}")
            return False, error_msg
        except smtplib.SMTPDataError as e:
            error_msg = f"Email data was rejected by the server: {str(e)}"
            print(f"❌ {error_msg}")
            return False, error_msg
        except smtplib.SMTPException as e:
            error_msg = f"SMTP error occurred: {str(e)}"
            print(f"❌ {error_msg}")
            return False, error_msg
        except Exception as e:
            error_msg = f"Unexpected error while sending email: {str(e)}"
            print(f"❌ {error_msg}")
            return False, error_msg
    
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
            
            # Send email with comprehensive error handling and verification
            print(f"📧 Attempting to send welcome email to {to_email}...")
            context = ssl.create_default_context()
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=30) as server:
                print("🔒 Establishing secure connection...")
                server.starttls(context=context)
                
                print("🔑 Authenticating with Gmail...")
                server.login(self.gmail_email, self.gmail_password)
                
                print("📤 Sending welcome email...")
                # sendmail returns a dictionary of failed recipients
                # Empty dict means all recipients succeeded
                failed_recipients = server.sendmail(self.gmail_email, [to_email], msg.as_string())
                
                if failed_recipients:
                    # Some recipients failed
                    failed_emails = list(failed_recipients.keys())
                    return False, f"Failed to send welcome email to: {', '.join(failed_emails)}"
                else:
                    # All recipients succeeded
                    print("✅ Welcome email sent successfully!")
                    return True, f"Welcome email successfully sent to {to_email}"
            
        except smtplib.SMTPAuthenticationError as e:
            error_msg = f"Gmail authentication failed: {str(e)}. Please verify your email and app password are correct."
            print(f"❌ {error_msg}")
            return False, error_msg
        except smtplib.SMTPRecipientsRefused as e:
            error_msg = f"Email address '{to_email}' was rejected by the server: {str(e)}"
            print(f"❌ {error_msg}")
            return False, error_msg
        except smtplib.SMTPSenderRefused as e:
            error_msg = f"Sender email '{self.gmail_email}' was rejected: {str(e)}"
            print(f"❌ {error_msg}")
            return False, error_msg
        except smtplib.SMTPDataError as e:
            error_msg = f"Email data was rejected by the server: {str(e)}"
            print(f"❌ {error_msg}")
            return False, error_msg
        except smtplib.SMTPException as e:
            error_msg = f"SMTP error occurred: {str(e)}"
            print(f"❌ {error_msg}")
            return False, error_msg
        except Exception as e:
            error_msg = f"Unexpected error while sending welcome email: {str(e)}"
            print(f"❌ {error_msg}")
            return False, error_msg
    
    def send_email(self, to_email: str, subject: str, body: str, is_html: bool = False) -> Tuple[bool, str]:
        """Send a general email with comprehensive error handling"""
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
            msg['Subject'] = subject
            
            # Attach body as HTML or plain text
            msg.attach(MIMEText(body, 'html' if is_html else 'plain'))
            
            # Send email with comprehensive error handling and verification
            print(f"📧 Attempting to send email to {to_email}...")
            print(f"📋 Subject: {subject}")
            
            context = ssl.create_default_context()
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=30) as server:
                print("🔒 Establishing secure connection...")
                server.starttls(context=context)
                
                print("🔑 Authenticating with Gmail...")
                server.login(self.gmail_email, self.gmail_password)
                
                print("📤 Sending email...")
                # sendmail returns a dictionary of failed recipients
                # Empty dict means all recipients succeeded
                failed_recipients = server.sendmail(self.gmail_email, [to_email], msg.as_string())
                
                if failed_recipients:
                    # Some recipients failed
                    failed_emails = list(failed_recipients.keys())
                    error_msg = f"Failed to send email to: {', '.join(failed_emails)}"
                    print(f"❌ {error_msg}")
                    return False, error_msg
                else:
                    # All recipients succeeded
                    success_msg = f"Email successfully sent to {to_email}"
                    print(f"✅ {success_msg}")
                    return True, success_msg
            
        except smtplib.SMTPAuthenticationError as e:
            error_msg = f"Gmail authentication failed: {str(e)}. Please verify your email and app password are correct."
            print(f"❌ {error_msg}")
            return False, error_msg
        except smtplib.SMTPRecipientsRefused as e:
            error_msg = f"Email address '{to_email}' was rejected by the server: {str(e)}"
            print(f"❌ {error_msg}")
            return False, error_msg
        except smtplib.SMTPSenderRefused as e:
            error_msg = f"Sender email '{self.gmail_email}' was rejected: {str(e)}"
            print(f"❌ {error_msg}")
            return False, error_msg
        except smtplib.SMTPDataError as e:
            error_msg = f"Email data was rejected by the server: {str(e)}"
            print(f"❌ {error_msg}")
            return False, error_msg
        except smtplib.SMTPException as e:
            error_msg = f"SMTP error occurred: {str(e)}"
            print(f"❌ {error_msg}")
            return False, error_msg
        except Exception as e:
            error_msg = f"Unexpected error while sending email: {str(e)}"
            print(f"❌ {error_msg}")
            return False, error_msg