import frappe
from frappe.email.doctype.notification.notification import Notification

print("--- Debugging Notification Trigger ---")

# 1. Verify Extension Loading
print(f"Checking extension loading...")
if hasattr(Notification, 'send_a_google_chat_msg'):
    print("✓ Extension is loaded on Notification class")
else:
    print("✗ Extension is NOT loaded on Notification class")
    # Force load for this test
    from gchat_integration.gchat_integration.notification_extension import extend_notification
    extend_notification()
    print("  (Force loaded extension for testing)")

# 2. Get the notification
notification_name = "test"
try:
    notification = frappe.get_doc("Notification", notification_name)
    print(f"✓ Found notification: {notification.name}")
    print(f"  Channel: {notification.channel}")
    print(f"  Webhook: {notification.google_chat_webhook}")
except Exception as e:
    print(f"✗ Could not find notification '{notification_name}': {e}")
    exit()

# 3. Get a reference document
doctype = notification.document_type
doc_name = frappe.db.get_value(doctype, {}, "name")
if not doc_name:
    print(f"✗ No {doctype} found to test with")
    # Create a dummy one in memory if possible, or just exit
    exit()

print(f"✓ Using reference document: {doctype} ({doc_name})")
doc = frappe.get_doc(doctype, doc_name)

# 4. Trigger send
print("Triggering notification.send()...")
try:
    # We call send directly to bypass event listening and just test the dispatch logic
    notification.send(doc)
    print("✓ notification.send() executed")
except Exception as e:
    print(f"✗ Error during notification.send(): {e}")

print("--- Check your logs now ---")
