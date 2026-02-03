"""
Quick verification script to check if Direct Message option is available.
Run with: bench --site sj.local execute gchat_integration.verify_dm_setup
"""

import frappe

def verify_dm_setup():
    """Verify that Direct Message option is available in Notification."""
    
    print("\n" + "="*60)
    print("Google Chat DM Setup Verification")
    print("="*60 + "\n")
    
    # Check if custom field exists
    try:
        cf = frappe.get_doc("Custom Field", "Notification-google_chat_type")
        print("✅ Custom field 'google_chat_type' exists")
        print(f"   Options: {cf.options}")
        
        if "Direct Message" in cf.options:
            print("   ✅ 'Direct Message' option is available")
        else:
            print("   ❌ 'Direct Message' option is MISSING")
            print("   Current options:", cf.options.split('\n'))
            
    except frappe.DoesNotExistError:
        print("❌ Custom field 'google_chat_type' does NOT exist")
        return
    
    # Check property setters
    print("\n" + "-"*60)
    print("Property Setters:")
    print("-"*60)
    
    try:
        ps = frappe.db.get_value(
            "Property Setter",
            {"doc_type": "Notification", "field_name": "column_break_5", "property": "depends_on"},
            "value"
        )
        print(f"✅ column_break_5 depends_on: {ps}")
        
        ps2 = frappe.db.get_value(
            "Property Setter",
            {"doc_type": "Notification", "field_name": "recipients", "property": "mandatory_depends_on"},
            "value"
        )
        print(f"✅ recipients mandatory_depends_on: {ps2}")
        
    except Exception as e:
        print(f"❌ Error checking property setters: {e}")
    
    # Check Google Chat Settings
    print("\n" + "-"*60)
    print("Google Chat Settings:")
    print("-"*60)
    
    try:
        settings = frappe.get_doc("Google Chat Settings", "Google Chat Settings")
        print(f"✅ Google Chat Settings exists")
        print(f"   Bot Enabled: {settings.enable_bot}")
        print(f"   Has Credentials: {'Yes' if settings.service_account_creds else 'No'}")
        
    except frappe.DoesNotExistError:
        print("⚠️  Google Chat Settings not found (will be created on first access)")
    
    print("\n" + "="*60)
    print("Next Steps:")
    print("="*60)
    print("1. Refresh your browser (Ctrl+F5 or Cmd+Shift+R)")
    print("2. Go to: Desk → Settings → Notification")
    print("3. Create new notification")
    print("4. Set Channel = 'Google Chat'")
    print("5. You should now see 'Direct Message' in Google Chat Type")
    print("6. When you select 'Direct Message', the Recipients field will appear")
    print("="*60 + "\n")

if __name__ == "__main__":
    verify_dm_setup()
