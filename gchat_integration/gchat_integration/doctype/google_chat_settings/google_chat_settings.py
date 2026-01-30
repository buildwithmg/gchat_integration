# Copyright (c) 2025, Frappe and contributors
# License: MIT. See LICENSE

import frappe
from frappe.model.document import Document


class GoogleChatSettings(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		bot_name: DF.Data | None
		default_notification_space: DF.Data | None
		enable_bot: DF.Check
		enable_system_notifications: DF.Check
		enable_workflow_approvals: DF.Check
		http_endpoint_url: DF.Data | None
		service_account_creds: DF.Code | None
		verification_token: DF.Data | None
	# end: auto-generated types

	def validate(self):
		"""Validate the settings."""
		if self.enable_bot and not self.service_account_creds:
			frappe.throw("Service Account JSON is required when Bot Integration is enabled")
		
		# Validate JSON format
		if self.service_account_creds:
			try:
				import json
				creds = json.loads(self.service_account_creds)
				required_fields = ["type", "project_id", "private_key", "client_email"]
				missing = [f for f in required_fields if f not in creds]
				if missing:
					frappe.throw(f"Service Account JSON is missing required fields: {', '.join(missing)}")
			except json.JSONDecodeError:
				frappe.throw("Invalid JSON format in Service Account JSON field")


def get_settings():
	"""Get Google Chat Settings singleton."""
	if not frappe.db.exists("Google Chat Settings", "Google Chat Settings"):
		settings = frappe.new_doc("Google Chat Settings")
		settings.insert(ignore_permissions=True)
		return settings
	return frappe.get_cached_doc("Google Chat Settings", "Google Chat Settings")


def is_bot_enabled():
	"""Check if bot integration is enabled."""
	try:
		settings = get_settings()
		return settings.enable_bot
	except Exception:
		return False


def is_workflow_approvals_enabled():
	"""Check if workflow approvals are enabled."""
	try:
		settings = get_settings()
		return settings.enable_bot and settings.enable_workflow_approvals
	except Exception:
		return False
