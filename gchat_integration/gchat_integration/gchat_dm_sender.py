# Copyright (c) 2025, Frappe and contributors
# License: MIT. See LICENSE

"""
Google Chat Direct Message Sender Module

This module provides functionality to send direct messages to users via Google Chat
using Service Account credentials with domain-wide delegation.

Requirements:
- Service Account with domain-wide delegation enabled
- OAuth Scopes: 
  - https://www.googleapis.com/auth/chat.spaces (for space setup)
  - https://www.googleapis.com/auth/chat.bot (for message sending)
"""

import frappe
from frappe import _
import json
import requests
from google.oauth2 import service_account
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


# OAuth Scopes
SCOPE_SPACES = ["https://www.googleapis.com/auth/chat.spaces"]
SCOPE_BOT = ["https://www.googleapis.com/auth/chat.bot"]


def get_service_account_credentials():
	"""
	Load Service Account credentials from Google Chat Settings.
	
	Returns:
		dict: Parsed service account credentials
	
	Raises:
		frappe.ValidationError: If credentials are not configured or invalid
	"""
	from gchat_integration.gchat_integration.doctype.google_chat_settings.google_chat_settings import (
		get_settings,
	)
	
	settings = get_settings()
	
	if not settings.service_account_creds:
		frappe.throw(_("Service Account credentials not configured in Google Chat Settings"))
	
	try:
		creds = json.loads(settings.service_account_creds)
		return creds
	except json.JSONDecodeError:
		frappe.throw(_("Invalid Service Account credentials format"))


def get_user_impersonation_creds(target_email):
	"""
	Create credentials to impersonate a specific user.
	This is required to setup DM spaces on behalf of the user.
	
	Args:
		target_email (str): Email address of the user to impersonate
	
	Returns:
		google.oauth2.service_account.Credentials: Impersonated credentials
	"""
	try:
		creds_dict = get_service_account_credentials()
		
		# Create credentials from service account
		creds = service_account.Credentials.from_service_account_info(
			creds_dict,
			scopes=SCOPE_SPACES
		)
		
		# Impersonate the target user
		return creds.with_subject(target_email)
	except Exception:
		frappe.logger().error(f"Google Chat DM - Failed to create impersonation credentials for {target_email}", exc_info=True)
		raise


def get_bot_creds():
	"""
	Create credentials for the Service Account itself (bot identity).
	Used for sending messages after space is established.
	
	Returns:
		google.oauth2.service_account.Credentials: Bot credentials
	"""
	try:
		creds_dict = get_service_account_credentials()
		
		return service_account.Credentials.from_service_account_info(
			creds_dict,
			scopes=SCOPE_BOT
		)
	except Exception:
		frappe.logger().error("Google Chat DM - Failed to create bot credentials", exc_info=True)
		raise


def get_or_create_dm_space(user_email):
	"""
	Get or create a DM space with a user using the spaces.setup API.
	
	This function:
	1. Impersonates the target user
	2. Calls spaces.setup() which returns the user's DM space with the bot
	3. Returns the space ID for message sending
	
	Args:
		user_email (str): Email address of the user
	
	Returns:
		str: Space ID (e.g., "spaces/AAAAxxxx") or None if failed
	"""
	try:
		# Impersonate the recipient user
		creds = get_user_impersonation_creds(user_email)
		service = build('chat', 'v1', credentials=creds)
		
		space_body = {
			'space': {
				'spaceType': 'DIRECT_MESSAGE',
				'singleUserBotDm': True
			}
		}
		
		frappe.logger().info(f"Google Chat DM: Setting up DM space for: {user_email}")
		
		result = service.spaces().setup(body=space_body).execute()
		
		space_name = result.get('name')
		frappe.logger().info(f"Google Chat DM: Space established: {space_name} for {user_email}")
		
		return space_name
	
	except HttpError as e:
		error_content = e.content.decode() if e.content else str(e)
		frappe.logger().error(f"Google Chat DM API Error for {user_email}: {error_content}")
		return None
	except Exception:
		frappe.logger().error(f"Google Chat DM Unexpected error setting up DM space for {user_email}", exc_info=True)
		return None


def send_dm_to_user(user_email, message_text, card=None):
	"""
	Send a direct message to a single user via Google Chat.
	
	Workflow:
	1. Get/create DM space by impersonating the user
	2. Get bot credentials
	3. Send message to the space
	
	Args:
		user_email (str): Email address of the recipient
		message_text (str): Plain text message to send
		card (dict, optional): Card v2 payload for rich formatting
	
	Returns:
		dict: API response if successful, None otherwise
	"""
	# Step 1: Get the DM space ID
	space_id = get_or_create_dm_space(user_email)
	
	if not space_id:
		frappe.logger().error(f"Google Chat DM - Could not establish DM space with {user_email}")
		return None
	
	# Step 2: Get bot credentials and refresh token
	try:
		creds = get_bot_creds()
		creds.refresh(Request())
	except Exception:
		frappe.logger().error("Google Chat DM - Failed to refresh bot credentials", exc_info=True)
		return None
	
	# Step 3: Prepare the message payload
	headers = {
		"Authorization": f"Bearer {creds.token}",
		"Content-Type": "application/json",
	}
	
	payload = {"text": message_text}
	if card:
		payload["cardsV2"] = card
	
	# Step 4: Send the message
	try:
		url = f"https://chat.googleapis.com/v1/{space_id}/messages"
		response = requests.post(url, headers=headers, json=payload)
		
		if response.status_code == 200:
			frappe.logger().info(f"Successfully sent DM to {user_email}")
			return response.json()
		else:
			frappe.logger().error(f"Google Chat DM - Failed to send DM to {user_email} ({response.status_code}): {response.text}")
			return None
	except Exception:
		frappe.logger().error(f"Google Chat DM - Request error while sending DM to {user_email}", exc_info=True)
		return None


def send_dm_to_multiple_users(user_emails, message_text, card=None):
	"""
	Send the same direct message to multiple users.
	
	Args:
		user_emails (list): List of email addresses
		message_text (str): Plain text message to send
		card (dict, optional): Card v2 payload for rich formatting
	
	Returns:
		dict: Summary of send results
			{
				"success": [list of successful emails],
				"failed": [list of failed emails]
			}
	"""
	results = {
		"success": [],
		"failed": []
	}
	
	for email in user_emails:
		try:
			response = send_dm_to_user(email, message_text, card)
			if response:
				results["success"].append(email)
			else:
				results["failed"].append(email)
		except Exception:
			frappe.logger().error(f"Google Chat DM - Exception sending DM to {email}", exc_info=True)
			results["failed"].append(email)
	
	frappe.logger().info(
		f"Batch DM send completed. Success: {len(results['success'])}, Failed: {len(results['failed'])}"
	)
	
	return results


def create_notification_card(title, subtitle, message, doc_url=None, buttons=None):
	"""
	Create a standard notification card for Google Chat.
	
	Args:
		title (str): Card header title
		subtitle (str): Card header subtitle
		message (str): Message text to display
		doc_url (str, optional): URL to the document (legacy, use buttons instead)
		buttons (list, optional): List of dicts with {"text": str, "url": str}
	
	Returns:
		list: Card v2 payload
	"""
	widgets = [
		{
			"textParagraph": {
				"text": message
			}
		}
	]
	
	# Handle legacy doc_url or new buttons list
	button_list = []
	if buttons:
		for b in buttons:
			button_list.append({
				"text": b.get("text"),
				"onClick": {
					"openLink": {
						"url": b.get("url")
					}
				}
			})
	elif doc_url:
		button_list.append({
			"text": "Open Document",
			"onClick": {
				"openLink": {
					"url": doc_url
				}
			}
		})

	if button_list:
		widgets.append({
			"buttonList": {
				"buttons": button_list
			}
		})
	
	return [{
		"cardId": "notification-card",
		"card": {
			"header": {
				"title": title,
				"subtitle": subtitle
			},
			"sections": [{
				"widgets": widgets
			}]
		}
	}]


def create_workflow_card(doctype, docname, message, status, actions=None, title=None):
	"""
	Create a workflow notification card with action buttons.
	
	Args:
		doctype (str): Document type
		docname (str): Document name
		message (str): Notification message
		status (str): Current workflow status
		actions (list, optional): List of dicts with {"text": str, "url": str}
		title (str, optional): Title of the document
	
	Returns:
		list: Card v2 payload with workflow actions
	"""
	# Format header and subtitle based on whether title is present
	if title and title != docname:
		header_title = title
		header_subtitle = f"{doctype}: {docname}"
	else:
		header_title = f"{doctype}: {docname}"
		header_subtitle = "Workflow Action Required"
	
	widgets = [
		{
			"decoratedText": {
				"topLabel": "Current Status",
				"text": f"<b>{status}</b>" if status else "N/A"
			}
		}
	]
	
	# Only add message if it's not the redundant link-only message
	# In Frappe, default workflow messages often contain a link to the form.
	# We'll rely on our explicit buttons instead.
	if message and not message.strip().startswith("<a href"):
		widgets.append({
			"textParagraph": {
				"text": message
			}
		})
	
	# Add action buttons
	if actions:
		button_list = []
		for action in actions:
			button_list.append({
				"text": action.get("text"),
				"onClick": {
					"openLink": {
						"url": action.get("url")
					}
				}
			})
		
		widgets.append({
			"buttonList": {
				"buttons": button_list
			}
		})
	
	return [{
		"cardId": "workflow-card",
		"card": {
			"header": {
				"title": header_title,
				"subtitle": header_subtitle
			},
			"sections": [{
				"widgets": widgets
			}]
		}
	}]
