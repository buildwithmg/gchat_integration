#!/usr/bin/env python3
"""
Test script for Google Chat DM notifications.
This script tests the DM functionality independently.

Usage:
    python test_dm_notification.py
"""

import sys
import os

# Add the frappe-bench apps path to Python path
sys.path.insert(0, '/home/kadmin/frappe-bench/apps')

def test_dm_send():
    """Test sending a DM to a single user."""
    import frappe
    from gchat_integration.gchat_integration.gchat_dm_sender import (
        send_dm_to_user,
        create_notification_card
    )
    
    # Initialize Frappe
    frappe.init(site='sj.local')  # Change to your site name
    frappe.connect()
    
    try:
        # Test user email
        test_email = "midhun@keystoneuae.com"
        
        print(f"Testing DM send to: {test_email}")
        
        # Create a test card
        card = create_notification_card(
            title="Test Notification",
            subtitle="From ERPNext",
            message="🔔 This is a test direct message from ERPNext Google Chat Integration!",
            doc_url="https://your-erp-site.com"
        )
        
        # Send DM
        result = send_dm_to_user(
            user_email=test_email,
            message_text="🔔 Test DM from ERPNext!",
            card=card
        )
        
        if result:
            print("✅ DM sent successfully!")
            print(f"Response: {result}")
        else:
            print("❌ Failed to send DM")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        frappe.destroy()


def test_batch_dm_send():
    """Test sending DM to multiple users."""
    import frappe
    from gchat_integration.gchat_integration.gchat_dm_sender import (
        send_dm_to_multiple_users,
        create_notification_card
    )
    
    # Initialize Frappe
    frappe.init(site='sj.local')  # Change to your site name
    frappe.connect()
    
    try:
        # Test user emails
        test_emails = [
            "midhun@keystoneuae.com",
            # Add more test emails here
        ]
        
        print(f"Testing batch DM send to: {', '.join(test_emails)}")
        
        # Create a test card
        card = create_notification_card(
            title="Batch Test Notification",
            subtitle="From ERPNext",
            message="🔔 This is a batch test direct message from ERPNext!",
            doc_url="https://your-erp-site.com"
        )
        
        # Send DMs
        results = send_dm_to_multiple_users(
            user_emails=test_emails,
            message_text="🔔 Batch Test DM from ERPNext!",
            card=card
        )
        
        print(f"\n✅ Success: {len(results['success'])}")
        for email in results['success']:
            print(f"   - {email}")
        
        if results['failed']:
            print(f"\n❌ Failed: {len(results['failed'])}")
            for email in results['failed']:
                print(f"   - {email}")
                
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        frappe.destroy()


if __name__ == "__main__":
    print("=" * 60)
    print("Google Chat DM Notification Test")
    print("=" * 60)
    print()
    
    # Test single DM
    print("Test 1: Single DM")
    print("-" * 60)
    test_dm_send()
    
    print()
    print("-" * 60)
    print()
    
    # Test batch DM
    print("Test 2: Batch DM")
    print("-" * 60)
    test_batch_dm_send()
    
    print()
    print("=" * 60)
    print("Tests completed")
    print("=" * 60)
