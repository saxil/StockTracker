#!/usr/bin/env python3
"""
Test script to verify email functionality in Docker container
"""
import os
import sys
from email_service import EmailService

def test_email_service():
    print("=" * 60)
    print("🐳 TESTING EMAIL SERVICE IN DOCKER CONTAINER")
    print("=" * 60)
    
    # Initialize email service
    email_service = EmailService()
    
    # Check configuration status
    print("\n📋 Configuration Status:")
    config_status = email_service.get_configuration_status()
    for key, value in config_status.items():
        print(f"  {key}: {value}")
    
    # Test connection if configured
    if email_service.is_configured():
        print("\n🔍 Testing SMTP connection...")
        success, message = email_service.test_connection()
        if success:
            print(f"✅ Connection test passed: {message}")
            
            # Test sending a welcome email to yourself
            test_email = email_service.gmail_email
            print(f"\n📧 Testing welcome email to {test_email}...")
            success, message = email_service.send_welcome_email(test_email, "Docker Test User")
            
            if success:
                print(f"✅ Welcome email test passed: {message}")
            else:
                print(f"❌ Welcome email test failed: {message}")
                
        else:
            print(f"❌ Connection test failed: {message}")
    else:
        print("\n⚠️  Email service not configured - skipping connection tests")
        print("To configure email service, set environment variables:")
        print("  - GMAIL_EMAIL: Your Gmail address")
        print("  - GMAIL_APP_PASSWORD: Your Gmail app password")
    
    print("\n" + "=" * 60)
    print("🏁 EMAIL SERVICE TEST COMPLETED")
    print("=" * 60)

if __name__ == "__main__":
    test_email_service()
