#!/usr/bin/env python3
"""
Comprehensive email diagnostics tool for troubleshooting SMTP issues
"""

import smtplib
import ssl
import socket
import os
from typing import Tuple, Dict

def test_network_connectivity() -> Dict[str, any]:
    """Test basic network connectivity to Gmail SMTP server"""
    print("🔍 Testing network connectivity...")
    
    results = {
        "dns_resolution": False,
        "port_443_open": False,
        "port_587_open": False,
        "port_465_open": False
    }
    
    # Test DNS resolution
    try:
        socket.gethostbyname("smtp.gmail.com")
        results["dns_resolution"] = True
        print("✅ DNS resolution: smtp.gmail.com resolved successfully")
    except socket.gaierror as e:
        print(f"❌ DNS resolution failed: {e}")
        return results
    
    # Test port connectivity
    for port_name, port in [("HTTPS (443)", 443), ("SMTP TLS (587)", 587), ("SMTP SSL (465)", 465)]:
        try:
            sock = socket.create_connection(("smtp.gmail.com", port), timeout=10)
            sock.close()
            results[f"port_{port}_open"] = True
            print(f"✅ {port_name}: Connection successful")
        except (socket.timeout, ConnectionRefusedError, OSError) as e:
            print(f"❌ {port_name}: Connection failed - {e}")
    
    return results

def test_ssl_context():
    """Test SSL context creation"""
    print("\n🔒 Testing SSL context...")
    
    try:
        context = ssl.create_default_context()
        print("✅ SSL context created successfully")
        print(f"   Protocol: {context.protocol}")
        print(f"   Check hostname: {context.check_hostname}")
        print(f"   Verify mode: {context.verify_mode}")
        return True
    except Exception as e:
        print(f"❌ SSL context creation failed: {e}")
        return False

def test_smtp_connection_methods():
    """Test different SMTP connection methods"""
    print("\n📧 Testing SMTP connection methods...")
    
    methods = [
        ("Method 1: SMTP + STARTTLS (Port 587)", test_smtp_starttls),
        ("Method 2: SMTP_SSL (Port 465)", test_smtp_ssl),
        ("Method 3: SMTP + STARTTLS with custom context", test_smtp_starttls_custom)
    ]
    
    for method_name, test_func in methods:
        print(f"\n{method_name}:")
        try:
            success, message = test_func()
            if success:
                print(f"✅ {message}")
                return method_name, True
            else:
                print(f"❌ {message}")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
    
    return None, False

def test_smtp_starttls() -> Tuple[bool, str]:
    """Test SMTP with STARTTLS on port 587"""
    try:
        context = ssl.create_default_context()
        with smtplib.SMTP("smtp.gmail.com", 587, timeout=30) as server:
            server.set_debuglevel(0)  # Set to 1 for verbose debugging
            server.starttls(context=context)
            return True, "SMTP STARTTLS connection successful"
    except smtplib.SMTPServerDisconnected as e:
        return False, f"Server disconnected: {e}"
    except smtplib.SMTPConnectError as e:
        return False, f"Connection error: {e}"
    except Exception as e:
        return False, f"Error: {e}"

def test_smtp_ssl() -> Tuple[bool, str]:
    """Test SMTP_SSL on port 465"""
    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=30, context=context) as server:
            server.set_debuglevel(0)
            return True, "SMTP_SSL connection successful"
    except Exception as e:
        return False, f"Error: {e}"

def test_smtp_starttls_custom() -> Tuple[bool, str]:
    """Test SMTP with custom SSL context"""
    try:
        # Create a more permissive SSL context for testing
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        
        with smtplib.SMTP("smtp.gmail.com", 587, timeout=30) as server:
            server.set_debuglevel(0)
            server.starttls(context=context)
            return True, "SMTP STARTTLS with custom context successful"
    except Exception as e:
        return False, f"Error: {e}"

def test_authentication():
    """Test Gmail authentication if credentials are available"""
    print("\n🔐 Testing Gmail authentication...")
    
    gmail_email = os.environ.get("GMAIL_EMAIL")
    gmail_password = os.environ.get("GMAIL_APP_PASSWORD")
    
    if not gmail_email or not gmail_password:
        print("⚠️  Gmail credentials not found in environment variables")
        print("   Set GMAIL_EMAIL and GMAIL_APP_PASSWORD to test authentication")
        return False
    
    print(f"📧 Email: {gmail_email}")
    print(f"🔑 App password: {'*' * len(gmail_password)} ({len(gmail_password)} chars)")
    
    # Try the working connection method from previous test
    try:
        context = ssl.create_default_context()
        with smtplib.SMTP("smtp.gmail.com", 587, timeout=30) as server:
            server.starttls(context=context)
            server.login(gmail_email, gmail_password)
            print("✅ Gmail authentication successful!")
            return True
    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ Authentication failed: {e}")
        print("\n💡 Troubleshooting tips:")
        print("   1. Ensure 2-factor authentication is enabled on your Google account")
        print("   2. Generate a new app password for 'Mail'")
        print("   3. Use the app password, not your regular password")
        print("   4. Remove any spaces from the app password")
        return False
    except Exception as e:
        print(f"❌ Connection error during authentication: {e}")
        return False

def get_system_info():
    """Get system information that might affect SMTP"""
    print("\n💻 System Information:")
    print(f"   OS: {os.name}")
    print(f"   Python version: {os.sys.version}")
    
    # Check for common networking tools
    try:
        import subprocess
        
        # Test if we can reach Google's DNS
        result = subprocess.run(["ping", "-n", "1", "8.8.8.8"], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("   ✅ Internet connectivity: Working")
        else:
            print("   ❌ Internet connectivity: Issues detected")
    except:
        print("   ⚠️  Could not test internet connectivity")

def run_full_diagnostics():
    """Run comprehensive email diagnostics"""
    print("🔧 Gmail SMTP Diagnostics Tool")
    print("=" * 50)
    
    # System info
    get_system_info()
    
    # Network tests
    network_results = test_network_connectivity()
    
    # SSL tests
    ssl_ok = test_ssl_context()
    
    # SMTP connection tests
    working_method, smtp_ok = test_smtp_connection_methods()
    
    # Authentication test
    auth_ok = test_authentication()
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 DIAGNOSTICS SUMMARY")
    print("=" * 50)
    
    print(f"🌐 Network connectivity: {'✅ OK' if network_results['dns_resolution'] else '❌ FAILED'}")
    print(f"🔒 SSL context: {'✅ OK' if ssl_ok else '❌ FAILED'}")
    print(f"📧 SMTP connection: {'✅ OK' if smtp_ok else '❌ FAILED'}")
    if working_method:
        print(f"   Working method: {working_method}")
    print(f"🔐 Authentication: {'✅ OK' if auth_ok else '❌ FAILED'}")
    
    if smtp_ok and auth_ok:
        print("\n🎉 All tests passed! Email service should work.")
    elif smtp_ok:
        print("\n⚠️  SMTP works but authentication failed. Check your Gmail credentials.")
    else:
        print("\n❌ SMTP connection failed. Check network/firewall settings.")
        print("\n💡 Possible solutions:")
        print("   1. Check your internet connection")
        print("   2. Disable Windows Firewall temporarily to test")
        print("   3. Check if your antivirus is blocking SMTP")
        print("   4. Try using a VPN")
        print("   5. Contact your network administrator")

if __name__ == "__main__":
    run_full_diagnostics()