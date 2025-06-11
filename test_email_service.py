#!/usr/bin/env python3
"""
Test script for the improved EmailService class
"""

from email_service import EmailService

def test_email_service():
    """Test the EmailService functionality"""
    print("=== Testing EmailService ===\n")
    
    # Initialize email service
    email_service = EmailService()
    
    # Test configuration status
    print("1. Configuration Status:")
    status = email_service.get_configuration_status()
    for key, value in status.items():
        print(f"   {key}: {value}")
    
    print(f"\n2. Is Configured: {email_service.is_configured()}")
    
    # Test connection
    print("\n3. Testing Connection:")
    connection_success, connection_msg = email_service.test_connection()
    print(f"   Success: {connection_success}")
    print(f"   Message: {connection_msg}")
    
    # Test reset email (this will show the improved error message)
    print("\n4. Testing Reset Email:")
    reset_success, reset_msg = email_service.send_reset_email(
        "test@example.com", 
        "TEST_TOKEN_123", 
        "TestUser"
    )
    print(f"   Success: {reset_success}")
    print(f"   Message: {reset_msg}")
    
    # Test welcome email
    print("\n5. Testing Welcome Email:")
    welcome_success, welcome_msg = email_service.send_welcome_email(
        "test@example.com", 
        "TestUser"
    )
    print(f"   Success: {welcome_success}")
    print(f"   Message: {welcome_msg}")

if __name__ == "__main__":
    test_email_service()
