# Copyright (c) 2025, Frappe and contributors
# License: MIT. See LICENSE

"""
Extension module to add Google Chat support to Frappe Notification DocType.
This module monkey patches the Notification class to add Google Chat functionality.
"""

import frappe
from frappe import _


def extend_notification():
	"""Extend the Notification DocType with Google Chat functionality."""
	from frappe.email.doctype.notification.notification import Notification
	from gchat_integration.gchat_integration.doctype.google_chat_webhook.google_chat_webhook import (
		send_google_chat_message,
	)

	# Store original method
	original_send_notification_by_channel = Notification.send_notification_by_channel

	def send_notification_by_channel_extended(self, doc, context):
		"""Extended method to support Google Chat channel."""
		try:
			frappe.logger().info(f"Notification triggered: {self.name}, Channel: {self.channel}")
			if self.channel == "Google Chat":
				frappe.logger().info(f"Processing Google Chat notification for: {self.name}")
				self.send_a_google_chat_msg(doc, context)
				
				# Additionally, if explicitly enabled, create a system notification
				if self.send_system_notification:
					self.create_system_notification(doc, context)
			else:
				# Call original method for other channels
				original_send_notification_by_channel(self, doc, context)
		except Exception as e:
			frappe.log_error(f"Failed to send Notification: {str(e)}")

	def send_a_google_chat_msg(self, doc, context):
		"""Send a message to Google Chat."""
		from frappe.email.doctype.notification.notification import (
			get_reference_doctype,
			get_reference_name,
		)
		from frappe.utils import get_url

		# Check Google Chat Type
		if self.google_chat_type == "Chatbot":
			from gchat_integration.gchat_integration.api import send_google_chat_bot_message
			
			space_id = self.google_chat_space
			if not space_id:
				frappe.log_error(f"No Space ID configured for notification: {self.name}", "Google Chat Integration")
				return

			message = frappe.render_template(self.message, context)
			
			send_google_chat_bot_message(
				space_id=space_id,
				message=message,
				reference_doctype=get_reference_doctype(doc),
				reference_name=get_reference_name(doc),
			)
			return
		
		elif self.google_chat_type == "Direct Message":
			from gchat_integration.gchat_integration.gchat_dm_sender import send_dm_to_multiple_users
			from gchat_integration.gchat_integration.doctype.google_chat_webhook.google_chat_webhook import (
				convert_html_to_gchat_text,
			)
			from frappe.utils import get_url_to_form
			
			frappe.log_error(f"Trace: Google Chat DM Processing {self.name}", "GChat DM Trace")
			
			# Get recipient email addresses
			recipient_emails = self.get_recipient_emails(doc, context)
			
			frappe.log_error(f"Trace: Google Chat DM Recipients: {recipient_emails}", "GChat DM Trace")
			
			if not recipient_emails:
				frappe.log_error(
					f"No valid recipient emails found for notification: {self.name}. Check if recipients have email addresses set.",
					"Google Chat DM - No Recipients"
				)
				return
			
			# Render and format message
			message = frappe.render_template(self.message, context)
			formatted_message = convert_html_to_gchat_text(message)
			
			# Create minimal card with document link (matching webhook style)
			reference_doctype = get_reference_doctype(doc)
			reference_name = get_reference_name(doc)
			doc_url = get_url_to_form(reference_doctype, reference_name)
			
			card = [{
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
			}]
			
			# Send DM to all recipients
			frappe.log_error(f"Trace: Google Chat DM Sending to {len(recipient_emails)} recipients", "GChat DM Trace")
			
			results = send_dm_to_multiple_users(
				user_emails=recipient_emails,
				message_text=formatted_message,
				card=card
			)
			
			# Log results
			if results["failed"]:
				frappe.log_error(
					f"Failed to send DM to: {', '.join(results['failed'])}",
					"Google Chat DM - Partial Failure"
				)
			
			frappe.log_error(f"Trace: Google Chat DM Send completed. Success: {len(results['success'])}, Failed: {len(results['failed'])}", "GChat DM Trace")
			return

		webhook = self.google_chat_webhook
		frappe.logger().info(f"Sending Google Chat message using webhook: {webhook}")
		
		if not webhook:
			frappe.log_error(f"No webhook configured for notification: {self.name}", "Google Chat Integration")
			return

		# Prepare message
		message = frappe.render_template(self.message, context)

		send_google_chat_message(
			webhook_url=webhook,
			message=message,
			reference_doctype=get_reference_doctype(doc),
			reference_name=get_reference_name(doc),
		)
	
	def get_recipient_emails(self, doc, context):
		"""
		Extract email addresses from notification recipients.
		Compatible with Frappe v16 native API.
		
		Args:
			doc: The document that triggered the notification
			context: Notification context
		
		Returns:
			list: List of email addresses
		"""
		recipients, cc, bcc = self.get_list_of_recipients(doc, context)
		emails = set(recipients)
		emails.update(cc)
		emails.update(bcc)

		# Filter out duplicates and invalid emails
		return [e for e in emails if e and "@" in e]



	# Monkey patch the methods
	Notification.send_notification_by_channel = send_notification_by_channel_extended
	Notification.send_a_google_chat_msg = send_a_google_chat_msg
	Notification.get_recipient_emails = get_recipient_emails



def get_notification_context():
	"""Hook to be called on app startup to extend Notification."""
	extend_notification()
