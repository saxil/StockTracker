import smtplib
import ssl
import os
from email.message import EmailMessage

def email_message(subject, body, to):
    """Send email with proper error handling and security"""
    
    # Get credentials from environment variables (more secure)
    user = os.environ.get("GMAIL_EMAIL", "lucifer.ai.288@gmail.com")
    password = os.environ.get("GMAIL_APP_PASSWORD", "mfbjcjevynjezpaz")
    
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
        print("Connecting to Gmail SMTP server...")
        with smtplib.SMTP("smtp.gmail.com", 587, timeout=30) as server:
            print("Starting TLS encryption...")
            server.starttls(context=context)
            
            print("Logging in...")
            server.login(user, password)
            
            print("Sending email...")
            server.send_message(msg)
            print("✅ Email sent successfully!")
            
    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ Authentication failed: {e}")
        print("Please check your email and app password.")
        print("Make sure 2FA is enabled and you're using an app password.")
        
    except smtplib.SMTPServerDisconnected as e:
        print(f"❌ Server disconnected: {e}")
        print("This could be due to:")
        print("- Network connectivity issues")
        print("- Firewall blocking SMTP")
        print("- Gmail temporarily blocking the connection")
        
    except smtplib.SMTPException as e:
        print(f"❌ SMTP error: {e}")
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def main():
    """Main function to get user input and send email"""
    print("=== Email Sender ===")
    to = input("Enter the recipient email: ")
    subject = input('Enter the subject: ')
    body = input("Enter the body: ")
    
    email_message(subject, body, to)

if __name__ == "__main__":
    main()