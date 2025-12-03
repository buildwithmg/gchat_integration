# Copyright (c) 2025, Frappe and contributors
# License: MIT. See LICENSE

"""
Installation and setup functions for gchat_integration app.
"""

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
from frappe.custom.doctype.property_setter.property_setter import make_property_setter


def after_install():
	"""Called after app installation to set up custom fields and configurations."""
	create_notification_custom_fields()
	update_notification_channel_options()
	create_notification_property_setters()
	setup_notification_extension()
	frappe.db.commit()


def create_notification_custom_fields():
	"""Create custom field for Google Chat Webhook in Notification DocType."""
	custom_fields = {
		"Notification": [
			{
				"fieldname": "google_chat_type",
				"label": "Google Chat Type",
				"fieldtype": "Select",
				"options": "Webhook\nChatbot",
				"default": "Webhook",
				"insert_after": "channel",
				"depends_on": 'eval:doc.channel=="Google Chat"',
				"description": "Choose how to send the notification"
			},
			{
				"fieldname": "google_chat_webhook",
				"label": "Google Chat Webhook",
				"fieldtype": "Link",
				"options": "Google Chat Webhook",
				"insert_after": "google_chat_type",
				"depends_on": 'eval:doc.channel=="Google Chat" && doc.google_chat_type=="Webhook"',
				"description": "Select the Google Chat Webhook to send notifications to",
				"mandatory_depends_on": 'eval:doc.channel=="Google Chat" && doc.google_chat_type=="Webhook"'
			}
		]
	}
	create_custom_fields(custom_fields, update=True)


def create_notification_property_setters():
	"""Create Property Setters to hide irrelevant fields for Google Chat."""
	# Hide Recipients section and table for Google Chat
	# Current depends_on: eval:doc.channel !="Slack"
	# New depends_on: eval:doc.channel !="Slack" && doc.channel !="Google Chat"
	
	make_property_setter(
		"Notification",
		"column_break_5",
		"depends_on",
		'eval:doc.channel !="Slack" && doc.channel !="Google Chat"',
		"Data"
	)
	
	make_property_setter(
		"Notification",
		"recipients",
		"mandatory_depends_on",
		'eval:doc.channel!=="Slack" && doc.channel!=="Google Chat" && !doc.send_to_all_assignees',
		"Data"
	)
	
	# We also want to hide Subject if it's not used, but let's check if we want to keep it.
	# Slack keeps it. Let's keep it for now to avoid confusion, or hide it if strictly following "relevant info".
	# If we hide it, we must ensure it's not mandatory.
	# Subject mandatory_depends_on: eval: in_list(['Email', 'Slack', 'System Notification'], doc.channel)
	# It already excludes Google Chat by default (since it's not in the list).
	# Subject depends_on: eval: in_list(['Email', 'Slack', 'System Notification'], doc.channel)
	# It already excludes Google Chat by default.
	# So Subject will be HIDDEN automatically for Google Chat. This is good.


def update_notification_channel_options():
	"""Add 'Google Chat' to the channel field options in Notification DocType."""
	try:
		# Get current options
		meta = frappe.get_meta("Notification")
		channel_field = meta.get_field("channel")
		
		if channel_field:
			current_options = channel_field.options or ""
			options_list = [opt.strip() for opt in current_options.split("\n") if opt.strip()]
			
			# Add Google Chat if not already present
			if "Google Chat" not in options_list:
				# Insert after Slack
				if "Slack" in options_list:
					slack_index = options_list.index("Slack")
					options_list.insert(slack_index + 1, "Google Chat")
				else:
					options_list.append("Google Chat")
				
				new_options = "\n".join(options_list)
				
				# Use Property Setter to update the options
				make_property_setter(
					"Notification",
					"channel",
					"options",
					new_options,
					"Text"
				)
				
				frappe.clear_cache(doctype="Notification")
	except Exception as e:
		frappe.log_error(f"Error updating Notification channel options: {str(e)}")


def setup_notification_extension():
	"""Set up the notification extension to enable Google Chat functionality."""
	try:
		from gchat_integration.gchat_integration.notification_extension import extend_notification
		extend_notification()
	except Exception as e:
		frappe.log_error(f"Error setting up notification extension: {str(e)}")

