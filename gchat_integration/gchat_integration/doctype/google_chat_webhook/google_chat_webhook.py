# Copyright (c) 2025, Frappe and contributors
# License: MIT. See LICENSE

import json

import requests

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import get_url_to_form

error_messages = {
	400: "400: Invalid request or malformed webhook URL",
	403: "403: Access forbidden",
	404: "404: Webhook URL not found",
	500: "500: Google Chat server error",
}


class GoogleChatWebhook(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		show_document_link: DF.Check
		webhook_name: DF.Data
		webhook_url: DF.Data
	# end: auto-generated types

	pass


def convert_html_to_gchat_text(html_content):
	"""Convert HTML content to Google Chat compatible text format."""
	if not html_content:
		return ""

	import re

	# Replace headers with bold text and newline
	html_content = re.sub(r'<h[1-6]>(.*?)</h[1-6]>', r'*\1*\n', html_content, flags=re.IGNORECASE)
	
	# Replace paragraphs with double newline
	html_content = re.sub(r'<p>(.*?)</p>', r'\1\n\n', html_content, flags=re.IGNORECASE)
	
	# Replace unordered lists
	html_content = re.sub(r'<ul>(.*?)</ul>', r'\1', html_content, flags=re.IGNORECASE | re.DOTALL)
	
	# Replace list items with bullet points
	html_content = re.sub(r'<li>(.*?)</li>', r'• \1\n', html_content, flags=re.IGNORECASE)
	# Handle unclosed list items if any (common in some HTML)
	html_content = re.sub(r'<li>(.*?)(?=<li>|</ul>)', r'• \1\n', html_content, flags=re.IGNORECASE | re.DOTALL)
	
	# Replace line breaks
	html_content = re.sub(r'<br\s*/?>', r'\n', html_content, flags=re.IGNORECASE)
	
	# Replace bold tags
	html_content = re.sub(r'<b>(.*?)</b>', r'*\1*', html_content, flags=re.IGNORECASE)
	html_content = re.sub(r'<strong>(.*?)</strong>', r'*\1*', html_content, flags=re.IGNORECASE)
	
	# Replace italic tags
	html_content = re.sub(r'<i>(.*?)</i>', r'_\1_', html_content, flags=re.IGNORECASE)
	html_content = re.sub(r'<em>(.*?)</em>', r'_\1_', html_content, flags=re.IGNORECASE)
	
	# Replace strike tags
	html_content = re.sub(r'<strike>(.*?)</strike>', r'~\1~', html_content, flags=re.IGNORECASE)
	html_content = re.sub(r'<s>(.*?)</s>', r'~\1~', html_content, flags=re.IGNORECASE)
	
	# Remove other tags but keep content
	html_content = re.sub(r'<[^>]+>', '', html_content)
	
	# Fix multiple newlines (max 2)
	html_content = re.sub(r'\n{3,}', r'\n\n', html_content)
	
	return html_content.strip()


def send_google_chat_message(webhook_url, message, reference_doctype, reference_name):
	"""Send a message to Google Chat using webhook URL.
	
	Args:
		webhook_url: Name of the Google Chat Webhook document
		message: Text message to send
		reference_doctype: DocType of the reference document
		reference_name: Name of the reference document
		
	Returns:
		"success" if message sent successfully, "error" otherwise
	"""
	gchat_url, show_link = frappe.db.get_value(
		"Google Chat Webhook", webhook_url, ["webhook_url", "show_document_link"]
	)

	if not gchat_url:
		frappe.log_error(f"Webhook URL not found for: {webhook_url}", _("Google Chat Webhook Error"))
		return "error"

	# Convert HTML message to Google Chat text format
	formatted_message = convert_html_to_gchat_text(message)

	# Build the Google Chat message
	# Google Chat webhooks support simple text or card format
	# Using the simpler card v2 format for better compatibility
	
	if show_link:
		doc_url = get_url_to_form(reference_doctype, reference_name)
		
		# Google Chat Card v2 format (simpler and more reliable)
		data = {
			"text": formatted_message,
			"cardsV2": [
				{
					"cardId": "document-link",
					"card": {
						"sections": [
							{
								"widgets": [
									{
										"buttonList": {
											"buttons": [
												{
													"text": reference_name,
													"onClick": {
														"openLink": {
															"url": doc_url
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
	else:
		# Simple text message
		data = {"text": formatted_message}

	try:
		frappe.logger().debug(f"Sending Google Chat message to: {gchat_url[:50]}...")
		frappe.logger().debug(f"Payload: {json.dumps(data)}")
		
		r = requests.post(gchat_url, json=data, headers={"Content-Type": "application/json; charset=UTF-8"})

		if not r.ok:
			error_msg = error_messages.get(r.status_code, f"{r.status_code}: {r.text}")
			frappe.log_error(f"Status: {r.status_code}\nResponse: {r.text}\nPayload: {json.dumps(data)}", _("Google Chat Webhook Error"))
			return "error"

		frappe.logger().info(f"Google Chat message sent successfully to webhook: {webhook_url}")
		return "success"
	except Exception as e:
		frappe.log_error(f"Exception: {str(e)}\nWebhook: {webhook_url}\nPayload: {json.dumps(data)}", _("Google Chat Webhook Error"))
		return "error"
