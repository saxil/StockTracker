import os
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def test_gmail_connection():
    """Test Gmail SMTP connection with detailed diagnostics"""
    
    gmail_email = os.environ.get("GMAIL_EMAIL")
    gmail_password = os.environ.get("GMAIL_APP_PASSWORD")
    
    print("=== Gmail Connection Test ===")
    print(f"Email configured: {bool(gmail_email)}")
    print(f"Password configured: {bool(gmail_password)}")
    
    if gmail_email:
        print(f"Email address: {gmail_email}")
    
    if gmail_password:
        print(f"Password length: {len(gmail_password)} characters")
        print(f"Password format (spaces removed): {gmail_password.replace(' ', '')}")
    
    if not gmail_email or not gmail_password:
        print("❌ Missing credentials")
        return False
    
    try:
        print("\n=== Testing SMTP Connection ===")
        context = ssl.create_default_context()
        
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            print("✓ Connected to smtp.gmail.com:587")
            
            server.starttls(context=context)
            print("✓ TLS connection established")
            
            # Try login with password as-is
            server.login(gmail_email, gmail_password)
            print("✓ Authentication successful!")
            
            return True
            
    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ Authentication failed: {e}")
        print("\nPossible solutions:")
        print("1. Verify 2-factor authentication is enabled on your Google account")
        print("2. Generate a new app password specifically for 'Mail'")
        print("3. Ensure the app password is 16 characters without spaces")
        print("4. Check that the email address is correct")
        return False
        
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

if __name__ == "__main__":
    test_gmail_connection()