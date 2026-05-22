# Copyright (c) 2025, Frappe and contributors
# License: MIT. See LICENSE

import frappe
from frappe import _
from gchat_integration.gchat_integration.doctype.google_chat_settings.google_chat_settings import (
	is_workflow_approvals_enabled,
)
from gchat_integration.gchat_integration.gchat_dm_sender import (
	send_dm_to_user,
	create_workflow_card,
)
from frappe.workflow.doctype.workflow_action.workflow_action import (
	get_next_possible_transitions,
	get_users_next_action_data,
	get_doc_workflow_state,
	get_common_email_args,
)


def notify_workflow_action(doc, method=None):
	"""
	Hook for 'after_insert' of Workflow Action.
	Sends a Direct Message to eligible users with interactive actions.
	"""
	if not is_workflow_approvals_enabled():
		return

	try:
		# Workflow Action doc provides reference_doctype and reference_name
		ref_doc = frappe.get_doc(doc.reference_doctype, doc.reference_name)
		workflow_name = frappe.model.workflow.get_workflow_name(doc.reference_doctype)
		
		# Get next possible transitions
		transitions = get_next_possible_transitions(workflow_name, doc.workflow_state, ref_doc)
		if not transitions:
			return

		# Get users who can perform these actions
		users_data = get_users_next_action_data(transitions, ref_doc)
		if not users_data:
			return

		# Get common message details (handles standard email templates if any)
		common_args = get_common_email_args(ref_doc)
		message_text = common_args.get("message")
		
		# Extract document title (using Frappe's native get_title if available)
		doc_title = None
		if hasattr(ref_doc, "get_title"):
			doc_title = ref_doc.get_title()
		
		if not doc_title:
			# Fallback to common fields
			doc_title = ref_doc.get("title") or ref_doc.get("subject") or ref_doc.get("custom_title")
		
		# If it's a template placeholder, try to render it
		if doc_title and "{" in doc_title:
			try:
				doc_title = frappe.render_template(doc_title, ref_doc.as_dict())
			except Exception:
				pass
		
		# For each user, send a DM
		for user_id, data in users_data.items():
			user_email = data.get("email")
			if not user_email:
				continue

			# Format actions for GChat card
			actions = []
			for action in data.get("possible_actions", []):
				actions.append({
					"text": action.get("action_name"),
					"url": action.get("action_link")
				})

			# Add "View Document" button
			from frappe.utils import get_url_to_form
			doc_url = get_url_to_form(doc.reference_doctype, doc.reference_name)
			actions.append({
				"text": _("View Document"),
				"url": doc_url
			})

			# Create GChat card
			card = create_workflow_card(
				doctype=doc.reference_doctype,
				docname=doc.reference_name,
				message=message_text,
				status=doc.workflow_state,
				actions=actions,
				title=doc_title
			)

			# Send DM in background
			# We send message_text="" here because the card already contains the info.
			# This avoids the redundant link text before the buttons.
			from frappe.utils.background_jobs import enqueue
			enqueue(
				send_dm_to_user,
				user_email=user_email,
				message_text="",
				card=card,
				queue="short"
			)

	except Exception:
		frappe.logger().error("Google Chat Workflow Notification Error", exc_info=True)
