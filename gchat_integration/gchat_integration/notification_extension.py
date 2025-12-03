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
			frappe.log_error(f"Google Chat Chatbot integration is not yet implemented for notification: {self.name}", "Google Chat Integration")
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

	# Monkey patch the methods
	Notification.send_notification_by_channel = send_notification_by_channel_extended
	Notification.send_a_google_chat_msg = send_a_google_chat_msg


def get_notification_context():
	"""Hook to be called on app startup to extend Notification."""
	extend_notification()
