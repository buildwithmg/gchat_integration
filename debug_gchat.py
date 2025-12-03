"""
Debug script to test Google Chat webhook integration.
Run this in bench console to test the notification system.

Usage:
    bench --site sj.local console
    >>> exec(open('apps/gchat_integration/debug_gchat.py').read())
"""

import frappe

def test_google_chat_webhook():
    """Test if Google Chat webhook is configured and working."""
    print("\n=== Google Chat Webhook Debug ===\n")
    
    # Check if Google Chat Webhook DocType exists
    print("1. Checking if Google Chat Webhook DocType exists...")
    webhooks = frappe.get_all("Google Chat Webhook", fields=["name", "webhook_name", "webhook_url"])
    if webhooks:
        print(f"   ✓ Found {len(webhooks)} webhook(s):")
        for wh in webhooks:
            print(f"     - {wh.webhook_name} ({wh.name})")
            print(f"       URL: {wh.webhook_url[:50]}...")
    else:
        print("   ✗ No Google Chat Webhooks found!")
        print("   → Create one at: Desk → GChat Integration → Google Chat Webhook")
        return
    
    # Check if Notification has Google Chat channel
    print("\n2. Checking Notification channel options...")
    meta = frappe.get_meta("Notification")
    channel_field = meta.get_field("channel")
    if channel_field:
        options = channel_field.options or ""
        if "Google Chat" in options:
            print("   ✓ 'Google Chat' is available in channel options")
        else:
            print("   ✗ 'Google Chat' NOT found in channel options!")
            print(f"   Current options: {options}")
    
    # Check if custom field exists
    print("\n3. Checking custom field 'google_chat_webhook'...")
    custom_field = frappe.db.exists("Custom Field", "Notification-google_chat_webhook")
    if custom_field:
        print("   ✓ Custom field exists")
    else:
        print("   ✗ Custom field NOT found!")
        print("   → Run: bench --site sj.local migrate")
    
    # Check notifications configured for Google Chat
    print("\n4. Checking Notifications configured for Google Chat...")
    notifications = frappe.get_all(
        "Notification",
        filters={"channel": "Google Chat"},
        fields=["name", "subject", "enabled", "google_chat_webhook", "document_type", "event"]
    )
    if notifications:
        print(f"   ✓ Found {len(notifications)} Google Chat notification(s):")
        for notif in notifications:
            status = "✓ Enabled" if notif.enabled else "✗ Disabled"
            print(f"\n     {status}: {notif.name}")
            print(f"       Subject: {notif.subject}")
            print(f"       DocType: {notif.document_type}")
            print(f"       Event: {notif.event}")
            print(f"       Webhook: {notif.google_chat_webhook or 'NOT SET!'}")
    else:
        print("   ✗ No notifications configured for Google Chat!")
        print("   → Create one at: Setup → Email → Notification")
    
    # Check if notification extension is loaded
    print("\n5. Checking if notification extension is loaded...")
    from frappe.email.doctype.notification.notification import Notification
    if hasattr(Notification, 'send_a_google_chat_msg'):
        print("   ✓ Notification extension is loaded!")
    else:
        print("   ✗ Notification extension NOT loaded!")
        print("   → Restart bench or run:")
        print("      from gchat_integration.gchat_integration.notification_extension import extend_notification")
        print("      extend_notification()")
    
    print("\n=== Debug Complete ===\n")

# Run the test
test_google_chat_webhook()
