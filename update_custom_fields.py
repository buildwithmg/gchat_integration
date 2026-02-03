#!/usr/bin/env python3
"""
Helper script to update custom fields for the Google Chat Integration app.
Run this after installing or updating the app to ensure all custom fields are in place.

Usage:
    cd /home/kadmin/frappe-bench/frappe-bench/apps/gchat_integration
    python update_custom_fields.py
"""

import sys
import os

# Add the frappe-bench apps path to Python path
sys.path.insert(0, '/home/kadmin/frappe-bench/apps')

def update_fields():
    """Update custom fields for the app."""
    import frappe
    from gchat_integration.gchat_integration.install import (
        create_notification_custom_fields,
        create_notification_property_setters,
        update_notification_channel_options,
        setup_notification_extension
    )
    
    # Initialize Frappe
    frappe.init(site='sj.local')  # Change to your site name
    frappe.connect()
    
    try:
        print("Updating Google Chat Integration custom fields...")
        print("-" * 60)
        
        # Update channel options
        print("1. Updating Notification channel options...")
        update_notification_channel_options()
        
        # Create custom fields
        print("2. Creating/updating custom fields...")
        create_notification_custom_fields()
        
        # Create property setters
        print("3. Creating/updating property setters...")
        create_notification_property_setters()
        
        # Setup notification extension
        print("4. Setting up notification extension...")
        setup_notification_extension()
        
        # Commit changes
        frappe.db.commit()
        
        print("-" * 60)
        print("✅ Custom fields updated successfully!")
        print()
        print("Next steps:")
        print("1. Go to Google Chat Settings and configure your Service Account")
        print("2. Create a new Notification with channel 'Google Chat'")
        print("3. Choose 'Direct Message' as the Google Chat Type")
        print("4. Add recipients and test!")
        
    except Exception as e:
        frappe.db.rollback()
        print(f"❌ Error updating custom fields: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        frappe.destroy()


if __name__ == "__main__":
    update_fields()
