import smtplib
import ssl
import os
from email.message import EmailMessage

def email_message_starttls(subject, body, to, user, password):
    """Send email using STARTTLS method (port 587)"""
    try:
        msg = EmailMessage()
        msg.set_content(body)
        msg['subject'] = subject
        msg['to'] = to
        msg['from'] = user
        
        context = ssl.create_default_context()
        
        print("Method 1: STARTTLS on port 587...")
        with smtplib.SMTP("smtp.gmail.com", 587, timeout=60) as server:
            server.starttls(context=context)
            server.login(user, password)
            server.send_message(msg)
            print("✅ Email sent successfully via STARTTLS!")
            return True
            
    except Exception as e:
        print(f"❌ STARTTLS method failed: {e}")
        return False

def email_message_ssl(subject, body, to, user, password):
    """Send email using direct SSL method (port 465)"""
    try:
        msg = EmailMessage()
        msg.set_content(body)
        msg['subject'] = subject
        msg['to'] = to
        msg['from'] = user
        
        context = ssl.create_default_context()
        
        print("Method 2: Direct SSL on port 465...")
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context, timeout=60) as server:
            server.login(user, password)
            server.send_message(msg)
            print("✅ Email sent successfully via SSL!")
            return True
            
    except Exception as e:
        print(f"❌ SSL method failed: {e}")
        return False

def email_message(subject, body, to):
    """Send email with multiple connection methods and proper error handling"""
    
    # Get credentials from environment variables (more secure)
    user = os.environ.get("GMAIL_EMAIL")
    password = os.environ.get("GMAIL_APP_PASSWORD")
    
    if not user or not password:
        print("❌ Email credentials not found!")
        print("Please set environment variables:")
        print("- GMAIL_EMAIL: Your Gmail address")
        print("- GMAIL_APP_PASSWORD: Your Gmail app password")
        print("\nTo set them in PowerShell:")
        print('$env:GMAIL_EMAIL="your.email@gmail.com"')
        print('$env:GMAIL_APP_PASSWORD="your16characterapppassword"')
        return False
    
    print(f"📧 Attempting to send email to: {to}")
    print(f"📧 From: {user}")
    
    # Try STARTTLS method first (most common)
    if email_message_starttls(subject, body, to, user, password):
        return True
    
    # If STARTTLS fails, try direct SSL
    print("\nRetrying with alternative method...")
    if email_message_ssl(subject, body, to, user, password):
        return True
    
    # Both methods failed
    print("\n❌ All email sending methods failed!")
    print("\n🔧 Troubleshooting suggestions:")
    print("1. Run 'python email_diagnostics.py' for detailed diagnostics")
    print("2. Check your firewall/antivirus settings")
    print("3. Verify your Gmail app password is correct")
    print("4. Try using a different network (mobile hotspot)")
    
    return False

def main():
    """Main function to get user input and send email"""
    print("=== Improved Email Sender ===")
    to = input("Enter the recipient email: ")
    subject = input('Enter the subject: ')
    body = input("Enter the body: ")
    
    success = email_message(subject, body, to)
    
    if not success:
        print("\n💡 Quick Setup Guide:")
        print("1. Enable 2FA on your Google account")
        print("2. Generate an app password: https://myaccount.google.com/apppasswords")
        print("3. Set environment variables with your credentials")

if __name__ == "__main__":
    main()
