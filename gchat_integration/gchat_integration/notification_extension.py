# Copyright (c) 2025, Frappe and contributors
# License: MIT. See LICENSE

import frappe
from frappe import _
from frappe.email.doctype.notification.notification import Notification


class CustomNotificationMixin:
	"""Mixin to add Google Chat support to Frappe Notification DocType."""

	def send_notification_by_channel(self, doc, context):
		"""Extended method to support Google Chat channel."""
		if self.channel == "Google Chat":
			from gchat_integration.gchat_integration.doctype.google_chat_settings.google_chat_settings import (
				is_bot_enabled,
			)

			if not is_bot_enabled():
				if self.send_system_notification:
					self.create_system_notification(doc, context)
				return

			try:
				frappe.logger().info(f"Processing Google Chat notification for: {self.name}")
				self.send_a_google_chat_msg(doc, context)
				if self.send_system_notification:
					self.create_system_notification(doc, context)
			except Exception:
				frappe.logger().error("Google Chat Notification Error", exc_info=True)
		else:
			super().send_notification_by_channel(doc, context)

	def send_a_google_chat_msg(self, doc, context):
		"""Send a message to Google Chat."""
		from frappe.email.doctype.notification.notification import (
			get_reference_doctype,
			get_reference_name,
		)
		from frappe.utils.background_jobs import enqueue

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
				queue="short",
			)
			return

		elif self.google_chat_type == "Direct Message":
			from gchat_integration.gchat_integration.gchat_dm_sender import (
				create_notification_card,
				send_dm_to_multiple_users,
			)
			from frappe.utils import get_url_to_form

			recipient_emails = self.get_recipient_emails(doc, context)
			if not recipient_emails:
				return

			message = frappe.render_template(self.message, context)
			subject = frappe.render_template(self.subject, context)

			reference_doctype = get_reference_doctype(doc)
			reference_name = get_reference_name(doc)
			doc_url = get_url_to_form(reference_doctype, reference_name)

			card = create_notification_card(
				title=subject,
				subtitle=f"{reference_doctype}: {reference_name}",
				message=message,
				buttons=[{"text": _("View Document"), "url": doc_url}],
			)

			enqueue(
				send_dm_to_multiple_users,
				user_emails=recipient_emails,
				message_text="",
				card=card,
				queue="short",
			)
			return

		webhook = self.google_chat_webhook
		if not webhook:
			return

		message = frappe.render_template(self.message, context)

		from gchat_integration.gchat_integration.doctype.google_chat_webhook.google_chat_webhook import (
			send_google_chat_message,
		)

		enqueue(
			send_google_chat_message,
			webhook_url=webhook,
			message=message,
			reference_doctype=get_reference_doctype(doc),
			reference_name=get_reference_name(doc),
			queue="short",
		)

	def get_recipient_emails(self, doc, context):
		recipients, cc, bcc = self.get_list_of_recipients(doc, context)
		emails = set(recipients)
		emails.update(cc)
		emails.update(bcc)
		return [e for e in emails if e and "@" in e]


def patch_verify_request():
	"""Apply resilient verify_request to handle URL decoding issues."""
	from frappe.utils import verified_command

	if hasattr(verified_command, "_original_verify_request"):
		return

	verified_command._original_verify_request = verified_command.verify_request

	import hmac
	from urllib.parse import urlencode, parse_qsl
	from frappe.utils.verified_command import _sign_message

	def resilient_verify_request():
		query_string = frappe.safe_decode(
			frappe.local.flags.signed_query_string or getattr(frappe.request, "query_string", None)
		)

		signature_string = "&_signature="
		if signature_string in query_string:
			params, given_signature = query_string.split(signature_string)

			if hmac.compare_digest(given_signature, _sign_message(params)):
				return True

			parsed_params = parse_qsl(params, keep_blank_values=True)
			reencoded_params = urlencode(parsed_params)

			if hmac.compare_digest(given_signature, _sign_message(reencoded_params)):
				return True

		return verified_command._original_verify_request()

	verified_command.verify_request = resilient_verify_request
