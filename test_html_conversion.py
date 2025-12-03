"""
Test script to verify HTML to Google Chat text conversion.
"""

import frappe
from gchat_integration.gchat_integration.doctype.google_chat_webhook.google_chat_webhook import convert_html_to_gchat_text

html_message = """
<h3>Order Overdue</h3>

<p>Transaction {{ doc.name }} has exceeded Due Date. Please take necessary action.</p>

<!-- show last comment -->
{% if comments %}
Last comment: {{ comments[-1].comment }} by {{ comments[-1].by }}
{% endif %}

<h4>Details</h4>

<ul>
<li>Customer: {{ doc.customer }}
<li>Amount: {{ doc.grand_total }}
</ul>
"""

print("--- Original HTML ---")
print(html_message)

print("\n--- Converted Text ---")
converted = convert_html_to_gchat_text(html_message)
print(converted)

print("\n--- Expected Output Check ---")
if "*Order Overdue*" in converted:
    print("✓ Header conversion working")
else:
    print("✗ Header conversion FAILED")

if "• Customer:" in converted:
    print("✓ List item conversion working")
else:
    print("✗ List item conversion FAILED")

if "\n\n" in converted:
    print("✓ Paragraph conversion working")
else:
    print("✗ Paragraph conversion FAILED")
