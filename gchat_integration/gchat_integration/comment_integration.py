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
		ref_doc_owner = frappe.db.get_value(doc.reference_doctype, doc.reference_name, "owner")
		if ref_doc_owner and ref_doc_owner != frappe.session.user and "@" in ref_doc_owner:
			recipients.add(ref_doc_owner)

		if not recipients:
			return

		# Prepare details
		from_user = get_fullname(doc.comment_email or doc.owner)
		# Pass mentions for more accurate bolding
		clean_content = clean_comment_content(doc.content or "", mentions=list(recipients))
		
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

	except Exception:
		frappe.logger().error("Google Chat Comment Notification Error", exc_info=True)


def clean_comment_content(content, mentions=None):
	"""
	Cleans HTML from comment content, specifically handling Quill mentions.
	Bolds @mentions for Google Chat cards using <b> tags.
	"""
	import re
	from frappe.utils import strip_html, get_fullname
	
	if not content:
		return ""
	
	# 1. Pre-cleaning malformed HTML fragments and handling newlines
	# Replace block-level tags and breaks with newlines
	# We use \n\n for block endings because GChat cards often collapse single \n
	content = re.sub(r'<(br|/p|/div|/li|/h[1-6])[^>]*>', '\n\n', content)
	
	# Remove attributes specifically (both double and single quoted)
	content = re.sub(r'[a-z-]+=(["\'])[^\1]*?\1', '', content)
	# Remove stray tag starts/ends that look like technical artifacts (e.g. Name" >)
	# Use a more conservative regex that won't eat into other text
	content = re.sub(r'\s*[a-zA-Z0-9_-]+="[^"]*"[^>]*>', ' ', content)
	content = re.sub(r'[^<>\n]*"[^>]*>', ' ', content)
	content = re.sub(r'&nbsp;', ' ', content)
	
	# 2. Strip all remaining HTML tags
	clean = strip_html(content)
	
	# 3. Bold Mentions using a placeholder system to avoid double-bolding
	# Resolve names to bold from the mention list
	names_to_bold = set()
	if mentions:
		for email in mentions:
			full_name = get_fullname(email)
			if full_name:
				names_to_bold.add(full_name)
			if "@" in email:
				# Also bold the email prefix
				names_to_bold.add(email.split("@")[0])

	# Sort by length descending to match longest possible names first
	sorted_names = sorted(list(names_to_bold), key=len, reverse=True)
	
	def bold_placeholder(text):
		return f"__BC_START__{text}__BC_END__"

	processed_text = clean
	
	# Pass A: Bold exactly the system-identified mentioned full names
	# This covers multi-word names like "Midhun George Geevar"
	for name in sorted_names:
		if name:
			# Only match if NOT preceded by __BC_START__
			# Use word boundary OR punctuation check for the end
			pattern = rf'(?<!__BC_START__)@{re.escape(name)}(?=\W|$)'
			processed_text = re.sub(pattern, bold_placeholder(f"@{name}"), processed_text)
	
	# Pass B: Fallback for any remaining single-word @mentions
	# (Safety fallback for manual user typing or unresolved mentions)
	# We don't greedily capture multi-word here to avoid bolding sentence starts.
	processed_text = re.sub(r'(?<!__BC_START__)(@[A-Za-z0-9._-]+)', lambda m: bold_placeholder(m.group(0)), processed_text)
	
	# Cleanup nested or redundant placeholders (Safety)
	processed_text = processed_text.replace("__BC_START____BC_START__", "__BC_START__")
	processed_text = processed_text.replace("__BC_END____BC_END__", "__BC_END__")
	
	# Final conversion to Google Chat HTML bold tags
	clean = processed_text.replace("__BC_START__", "<b>").replace("__BC_END__", "</b>")
	
	# 4. Final safety cleanup
	# Collapse excessive newlines (3+ -> 2)
	clean = re.sub(r'\n{3,}', '\n\n', clean)
	
	# Remove leftover quotes, brackets, or corrupted tag fragments at start/end
	clean = re.sub(r'^[">\'\s]+', '', clean)
	clean = re.sub(r'[">\'\s]+$', '', clean)
	
	return clean.strip()
