# Copyright (c) 2025, Frappe and contributors
# License: MIT. See LICENSE

import frappe
from frappe import _
from frappe.desk.notifications import extract_mentions
from gchat_integration.gchat_integration.gchat_dm_sender import (
	send_dm_to_user,
	create_notification_card,
)
from gchat_integration.gchat_integration.doctype.google_chat_settings.google_chat_settings import (
	is_bot_enabled,
)
from frappe.utils import get_fullname, strip_html


def notify_comment(doc, method=None):
	"""
	Hook for 'after_insert' of Comment.
	Sends a Direct Message to mentioned users.
	"""
	if not is_bot_enabled():
		return

	if doc.comment_type != "Comment":
		return

	try:
		# Extract mentions (@user)
		mentions = extract_mentions(doc.content or "")
		
		# Recipients to notify
		recipients = set()
		if mentions:
			for mention in mentions:
				# mention is usually the user ID (email)
				if mention != frappe.session.user:
					recipients.add(mention)
		
		# Optionally notify document owner if they are not the one who commented
		# For now, we'll only notify owner if no one else is mentioned 
		# OR we can always notify the owner if they aren't the commenter.
		# Let's check common logic: if it's a comment on their doc, they should know.
		ref_doc_owner = frappe.db.get_value(doc.reference_doctype, doc.reference_name, "owner")
		if ref_doc_owner and ref_doc_owner != frappe.session.user and "@" in ref_doc_owner:
			recipients.add(ref_doc_owner)

		if not recipients:
			return

		# Prepare details
		from_user = get_fullname(doc.comment_email or doc.owner)
		clean_content = strip_html(doc.content or "")
		if len(clean_content) > 500:
			clean_content = clean_content[:497] + "..."

		from frappe.utils import get_url_to_form
		doc_url = get_url_to_form(doc.reference_doctype, doc.reference_name)

		# Header title: [Commenter Name] commented on [DocType]: [DocID]
		header_title = _("{0} commented").format(from_user)
		header_subtitle = f"{doc.reference_doctype}: {doc.reference_name}"

		# Create GChat card
		card = create_notification_card(
			title=header_title,
			subtitle=header_subtitle,
			message=clean_content,
			buttons=[
				{"text": _("View Document"), "url": doc_url}
			]
		)

		# Send DM to each recipient in background
		from frappe.utils.background_jobs import enqueue
		for user_email in recipients:
			if "@" not in user_email:
				continue
				
			frappe.logger().info(f"Enqueuing Comment DM to {user_email} for {doc.reference_name}")
			enqueue(
				send_dm_to_user,
				user_email=user_email,
				message_text="",
				card=card,
				queue="short"
			)

	except Exception as e:
		frappe.log_error(f"Failed to send Google Chat Comment Notification: {str(e)}", "Google Chat Integration")
