import smtplib
import ssl
import os
from email.message import EmailMessage

import smtplib
import ssl
import os
from email.message import EmailMessage

def email_message(subject, body, to):
    """Send email with proper error handling and security - returns True only if email is actually sent"""
    
    # Get credentials from environment variables (more secure)
    user = os.environ.get("GMAIL_EMAIL")
    password = os.environ.get("GMAIL_APP_PASSWORD")
    
    # Check if credentials are available
    if not user or not password:
        print("❌ Email credentials not configured")
        print("Please set GMAIL_EMAIL and GMAIL_APP_PASSWORD environment variables")
        return False
    
    print(f"📧 Sending email from: {user}")
    print(f"📧 Sending email to: {to}")
    print(f"📋 Subject: {subject}")
    
    try:
        # Create message
        msg = EmailMessage()
        msg.set_content(body)
        msg['subject'] = subject
        msg['to'] = to
        msg['from'] = user
        
        # Create secure SSL context
        context = ssl.create_default_context()
        
        # Connect and send email with proper error handling
        print("🔒 Connecting to Gmail SMTP server...")
        with smtplib.SMTP("smtp.gmail.com", 587, timeout=30) as server:
            print("🔐 Starting TLS encryption...")
            server.starttls(context=context)
            
            print("🔑 Logging in...")
            server.login(user, password)
            
            print("📤 Sending email...")
            # send_message returns a dictionary of failed recipients
            # Empty dict means all recipients succeeded
            failed_recipients = server.send_message(msg)
            
            if failed_recipients:
                # Some recipients failed
                failed_emails = list(failed_recipients.keys())
                print(f"❌ Failed to send email to: {', '.join(failed_emails)}")
                return False
            else:
                # All recipients succeeded
                print("✅ Email sent successfully!")
                return True
            
    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ Authentication failed: {e}")
        print("Please check your email and app password.")
        print("Make sure 2FA is enabled and you're using an app password.")
        return False
        
    except smtplib.SMTPRecipientsRefused as e:
        print(f"❌ Recipient email address was rejected: {e}")
        print("Please check if the recipient email address is valid.")
        return False
        
    except smtplib.SMTPSenderRefused as e:
        print(f"❌ Sender email address was rejected: {e}")
        print("Please check your Gmail email address.")
        return False
        
    except smtplib.SMTPDataError as e:
        print(f"❌ Email data was rejected by the server: {e}")
        return False
        
    except smtplib.SMTPServerDisconnected as e:
        print(f"❌ Server disconnected: {e}")
        print("This could be due to:")
        print("- Network connectivity issues")
        print("- Firewall blocking SMTP")
        print("- Gmail temporarily blocking the connection")
        return False
        
    except smtplib.SMTPException as e:
        print(f"❌ SMTP error: {e}")
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def main():
    """Main function to get user input and send email"""
    print("=== Email Sender ===")
    to = input("Enter the recipient email: ")
    subject = input('Enter the subject: ')
    body = input("Enter the body: ")
    
    email_message(subject, body, to)

if __name__ == "__main__":
    main()