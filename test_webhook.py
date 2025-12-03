"""
Quick test script to verify Google Chat webhook is working.
Paste this in bench console to test the webhook directly.
"""

import frappe
import json
import requests

# Test the webhook
webhook_name = "test"  # Replace with your webhook name

# Get webhook URL
webhook_doc = frappe.get_doc("Google Chat Webhook", webhook_name)
print(f"Testing webhook: {webhook_doc.webhook_name}")
print(f"URL: {webhook_doc.webhook_url[:50]}...")

# Test 1: Simple text message
print("\n--- Test 1: Simple text message ---")
data1 = {"text": "Test message from ERPNext - Simple Text"}
try:
    r1 = requests.post(webhook_doc.webhook_url, json=data1)
    print(f"Status: {r1.status_code}")
    print(f"Response: {r1.text}")
    if r1.ok:
        print("✓ Simple text message sent successfully!")
    else:
        print(f"✗ Failed: {r1.status_code} - {r1.text}")
except Exception as e:
    print(f"✗ Exception: {e}")

# Test 2: Message with card (button)
print("\n--- Test 2: Message with card and button ---")
data2 = {
    "text": "Test message with button",
    "cardsV2": [
        {
            "cardId": "test-card",
            "card": {
                "sections": [
                    {
                        "widgets": [
                            {
                                "buttonList": {
                                    "buttons": [
                                        {
                                            "text": "Click me!",
                                            "onClick": {
                                                "openLink": {
                                                    "url": "https://www.example.com"
                                                }
                                            }
                                        }
                                    ]
                                }
                            }
                        ]
                    }
                ]
            }
        }
    ]
}
try:
    r2 = requests.post(webhook_doc.webhook_url, json=data2)
    print(f"Status: {r2.status_code}")
    print(f"Response: {r2.text}")
    if r2.ok:
        print("✓ Card message sent successfully!")
    else:
        print(f"✗ Failed: {r2.status_code} - {r2.text}")
except Exception as e:
    print(f"✗ Exception: {e}")

print("\n--- Test Complete ---")
print("Check your Google Chat space for the test messages!")
