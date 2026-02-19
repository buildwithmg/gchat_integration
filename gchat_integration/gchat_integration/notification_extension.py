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
		from frappe.utils.background_jobs import enqueue

		# Check Google Chat Type
		if self.google_chat_type == "Chatbot":
			from gchat_integration.gchat_integration.api import send_google_chat_bot_message
			
			space_id = self.google_chat_space
			if not space_id:
				return

			message = frappe.render_template(self.message, context)
			
			enqueue(
				send_google_chat_bot_message,
				space_id=space_id,
				message=message,
				reference_doctype=get_reference_doctype(doc),
				reference_name=get_reference_name(doc),
				queue="short"
			)
			return
		
		elif self.google_chat_type == "Direct Message":
			from gchat_integration.gchat_integration.gchat_dm_sender import (
				send_dm_to_multiple_users,
				create_notification_card,
			)
			from frappe.utils import get_url_to_form
			
			# Get recipient email addresses
			recipient_emails = self.get_recipient_emails(doc, context)
			
			if not recipient_emails:
				return
			
			# Render message and subject
			message = frappe.render_template(self.message, context)
			subject = frappe.render_template(self.subject, context)
			
			reference_doctype = get_reference_doctype(doc)
			reference_name = get_reference_name(doc)
			doc_url = get_url_to_form(reference_doctype, reference_name)
			
			# Create card using the style helper
			# Subject as Header, Message as Body
			card = create_notification_card(
				title=subject,
				subtitle=f"{reference_doctype}: {reference_name}",
				message=message,
				buttons=[{
					"text": _("View Document"),
					"url": doc_url
				}]
			)
			
			# Send DM to all recipients in background
			enqueue(
				send_dm_to_multiple_users,
				user_emails=recipient_emails,
				message_text="", # Content is in the card
				card=card,
				queue="short"
			)
			return

		webhook = self.google_chat_webhook
		if not webhook:
			return

		# Prepare message
		message = frappe.render_template(self.message, context)

		enqueue(
			send_google_chat_message,
			webhook_url=webhook,
			message=message,
			reference_doctype=get_reference_doctype(doc),
			reference_name=get_reference_name(doc),
			queue="short"
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

	# Apply resilient verify_request to handle URL decoding issues (common with GChat and some email clients)
	from frappe.utils import verified_command
	
	if not hasattr(verified_command, "_original_verify_request"):
		verified_command._original_verify_request = verified_command.verify_request
		
		def resilient_verify_request():
			"""
			Extended verify_request that handles partially decoded characters 
			(like '@' or ':') in the query string by re-encoding them 
			if the initial verification fails.
			"""
			import hmac
			from urllib.parse import urlencode, parse_qsl
			from frappe.utils.verified_command import _sign_message
			
			query_string = frappe.safe_decode(
				frappe.local.flags.signed_query_string or getattr(frappe.request, "query_string", None)
			)
			
			signature_string = "&_signature="
			if signature_string in query_string:
				params, given_signature = query_string.split(signature_string)
				
				# 1. Try original (as-is)
				if hmac.compare_digest(given_signature, _sign_message(params)):
					return True
				
				# 2. Try re-encoded (handles cases where browser/client decodes some chars)
				# parse_qsl handles '+' and '%20' consistently
				parsed_params = parse_qsl(params, keep_blank_values=True)
				reencoded_params = urlencode(parsed_params)
				
				if hmac.compare_digest(given_signature, _sign_message(reencoded_params)):
					return True
					
			# 3. Fallback to original (which handles the error response)
			return verified_command._original_verify_request()
		
		# Patch the module function
		verified_command.verify_request = resilient_verify_request



def get_notification_context():
	"""Hook to be called on app startup to extend Notification."""
	extend_notification()
