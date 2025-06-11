#!/usr/bin/env python3
"""
Email Diagnostics Tool for Gmail SMTP Connection Issues
"""

import smtplib
import ssl
import socket
import os
import sys
from email.mime.text import MIMEText

def test_network_connectivity():
    """Test basic network connectivity to Gmail SMTP server"""
    print("=== Network Connectivity Test ===")
    
    try:
        # Test DNS resolution
        print("1. Testing DNS resolution for smtp.gmail.com...")
        import socket
        ip = socket.gethostbyname('smtp.gmail.com')
        print(f"   ✅ DNS resolution successful: {ip}")
        
        # Test port connectivity
        print("2. Testing port 587 connectivity...")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        result = sock.connect_ex(('smtp.gmail.com', 587))
        sock.close()
        
        if result == 0:
            print("   ✅ Port 587 is accessible")
            return True
        else:
            print("   ❌ Port 587 is blocked or unreachable")
            return False
            
    except Exception as e:
        print(f"   ❌ Network connectivity error: {e}")
        return False

def test_ssl_connection():
    """Test SSL/TLS connection to Gmail"""
    print("\n=== SSL/TLS Connection Test ===")
    
    try:
        print("1. Testing basic SMTP connection...")
        with smtplib.SMTP('smtp.gmail.com', 587, timeout=30) as server:
            print("   ✅ Basic SMTP connection established")
            
            print("2. Testing STARTTLS...")
            context = ssl.create_default_context()
            server.starttls(context=context)
            print("   ✅ STARTTLS successful")
            
            print("3. Testing EHLO response...")
            server.ehlo()
            print("   ✅ EHLO successful")
            
            return True
            
    except smtplib.SMTPServerDisconnected as e:
        print(f"   ❌ Server disconnected: {e}")
        print("   💡 This often indicates firewall or antivirus blocking")
        return False
    except ssl.SSLError as e:
        print(f"   ❌ SSL/TLS error: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Connection error: {e}")
        return False

def test_authentication():
    """Test Gmail authentication"""
    print("\n=== Authentication Test ===")
    
    email = os.environ.get("GMAIL_EMAIL")
    password = os.environ.get("GMAIL_APP_PASSWORD")
    
    if not email or not password:
        print("   ❌ Environment variables not set")
        print("   Please set GMAIL_EMAIL and GMAIL_APP_PASSWORD")
        return False
    
    print(f"   Email: {email}")
    print(f"   Password length: {len(password)} characters")
    
    try:
        print("   Testing authentication...")
        context = ssl.create_default_context()
        
        with smtplib.SMTP('smtp.gmail.com', 587, timeout=30) as server:
            server.starttls(context=context)
            server.login(email, password)
            print("   ✅ Authentication successful")
            return True
            
    except smtplib.SMTPAuthenticationError as e:
        print(f"   ❌ Authentication failed: {e}")
        print("   💡 Check your email and app password")
        return False
    except Exception as e:
        print(f"   ❌ Error during authentication: {e}")
        return False

def test_alternative_methods():
    """Test alternative connection methods"""
    print("\n=== Alternative Connection Methods ===")
    
    # Method 1: Different timeout settings
    print("1. Testing with extended timeout...")
    try:
        with smtplib.SMTP('smtp.gmail.com', 587, timeout=60) as server:
            server.set_debuglevel(0)  # Disable debug for cleaner output
            context = ssl.create_default_context()
            server.starttls(context=context)
            print("   ✅ Extended timeout method works")
    except Exception as e:
        print(f"   ❌ Extended timeout failed: {e}")
    
    # Method 2: Using SMTP_SSL (direct SSL connection)
    print("2. Testing SMTP_SSL on port 465...")
    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context, timeout=30) as server:
            print("   ✅ SMTP_SSL method works")
    except Exception as e:
        print(f"   ❌ SMTP_SSL failed: {e}")

def check_system_info():
    """Check system information that might affect SMTP"""
    print("\n=== System Information ===")
    
    print(f"   Python version: {sys.version}")
    print(f"   Operating system: {os.name}")
    
    # Check if running in corporate environment
    proxy_vars = ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy']
    proxy_found = False
    for var in proxy_vars:
        if os.environ.get(var):
            print(f"   ⚠️  Proxy detected: {var}={os.environ.get(var)}")
            proxy_found = True
    
    if not proxy_found:
        print("   ✅ No proxy environment variables found")

def provide_solutions():
    """Provide common solutions for SMTP issues"""
    print("\n=== Common Solutions ===")
    print("1. 🔐 Gmail App Password Setup:")
    print("   - Enable 2-factor authentication on your Google account")
    print("   - Go to Google Account settings > Security > App passwords")
    print("   - Generate a new app password for 'Mail'")
    print("   - Use the 16-character app password (no spaces)")
    
    print("\n2. 🛡️ Firewall/Antivirus:")
    print("   - Temporarily disable Windows Defender Firewall")
    print("   - Temporarily disable antivirus real-time protection")
    print("   - Add Python to firewall exceptions")
    
    print("\n3. 🌐 Network Issues:")
    print("   - Try using mobile hotspot instead of office/school network")
    print("   - Check if your ISP blocks SMTP ports")
    print("   - Try using VPN if corporate firewall blocks SMTP")
    
    print("\n4. 🔧 Code Alternatives:")
    print("   - Use SMTP_SSL on port 465 instead of STARTTLS on 587")
    print("   - Increase connection timeout values")
    print("   - Use OAuth2 instead of app passwords (advanced)")

def main():
    """Run comprehensive email diagnostics"""
    print("🔍 Gmail SMTP Diagnostics Tool")
    print("=" * 50)
    
    # Run all tests
    network_ok = test_network_connectivity()
    ssl_ok = test_ssl_connection() if network_ok else False
    auth_ok = test_authentication() if ssl_ok else False
    
    if not network_ok:
        print("\n🚨 NETWORK ISSUE DETECTED")
        print("Your network connection to Gmail SMTP is blocked.")
    elif not ssl_ok:
        print("\n🚨 SSL/TLS ISSUE DETECTED")
        print("SSL/TLS connection is failing.")
    elif not auth_ok:
        print("\n🚨 AUTHENTICATION ISSUE DETECTED")
        print("Login credentials are incorrect.")
    else:
        print("\n✅ ALL TESTS PASSED")
        print("Your email configuration should work!")
    
    # Test alternative methods
    test_alternative_methods()
    
    # Show system info
    check_system_info()
    
    # Provide solutions
    provide_solutions()

if __name__ == "__main__":
    main()
