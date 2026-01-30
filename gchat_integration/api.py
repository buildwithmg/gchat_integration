import frappe
from frappe import _
import json

@frappe.whitelist(allow_guest=True)
def handle_google_chat_event():
    """
    Handle incoming events from Google Chat.
    Endpoint: /api/method/gchat_integration.api.handle_google_chat_event
    """
    try:
        # Check if bot is enabled
        from gchat_integration.gchat_integration.doctype.google_chat_settings.google_chat_settings import is_bot_enabled
        if not is_bot_enabled():
            frappe.log_error("Google Chat Bot is not enabled in settings", "Google Chat Integration")
            return {"text": "Bot integration is not enabled"}
        
        if frappe.request.method != "POST":
            return

        data = frappe.get_request_header("Content-Type")
        if "application/json" not in data:
            data = json.loads(frappe.request.get_data())
        else:
            data = frappe.request.json

        if not data:
            return

        event_type = data.get("type")
        
        if event_type == "ADDED_TO_SPACE":
            return on_added_to_space(data)
        elif event_type == "REMOVED_FROM_SPACE":
            return on_removed_from_space(data)
        elif event_type == "MESSAGE":
            return on_message(data)
        elif event_type == "CARD_CLICKED":
            return on_card_clicked(data)
        else:
            return {"text": "Unknown event type"}

    except Exception as e:
        frappe.log_error(f"Google Chat Event Error: {str(e)}", "Google Chat Integration")
        return {"text": "Error processing event"}

def on_added_to_space(data):
    """Handle ADDED_TO_SPACE event."""
    user_name = data.get("user", {}).get("displayName", "User")
    space_name = data.get("space", {}).get("displayName", "this space")
    
    return {
        "text": f"Thanks for adding me to {space_name}, {user_name}!"
    }

def on_removed_from_space(data):
    """Handle REMOVED_FROM_SPACE event."""
    # Cleanup if needed
    return

def on_message(data):
    """Handle MESSAGE event."""
    # Echo back for now or handle commands
    message_text = data.get("message", {}).get("text", "")
    
    return {
        "text": f"You said: {message_text}"
    }

def on_card_clicked(data):
    """Handle CARD_CLICKED event (e.g. Workflow Approvals)."""
    action_method = data.get("action", {}).get("actionMethodName")
    parameters = data.get("action", {}).get("parameters", [])
    
    if action_method == "approve_workflow":
        return handle_workflow_action(parameters, "Approve")
    elif action_method == "reject_workflow":
        return handle_workflow_action(parameters, "Reject")
    
    return {"text": "Action received"}

def handle_workflow_action(parameters, action):
    """Process workflow action."""
    # Check if workflow approvals are enabled
    from gchat_integration.gchat_integration.doctype.google_chat_settings.google_chat_settings import is_workflow_approvals_enabled
    if not is_workflow_approvals_enabled():
        return {"text": "Workflow approvals are not enabled"}
    
    # parameters is a list of dicts: [{'key': 'doctype', 'value': ...}, {'key': 'docname', 'value': ...}]
    doctype = None
    docname = None
    
    for param in parameters:
        if param.get("key") == "doctype":
            doctype = param.get("value")
        elif param.get("key") == "docname":
            docname = param.get("value")
            
    if doctype and docname:
        frappe.logger().info(f"Processing workflow action {action} for {doctype} {docname}")
        # frappe.get_doc(doctype, docname).apply_workflow_transition(action) # Example
        return {"text": f"Workflow {action} action processed for {docname}"}
        
    return {"text": f"Workflow {action} action processed (missing parameters)"}

def send_google_chat_bot_message(space_id, message, reference_doctype, reference_name):
    """
    Send a message to Google Chat Space using Chat API.
    Requires Service Account credentials.
    """
    frappe.logger().info(f"Preparing to send Bot message to Space: {space_id}")
    
    # Convert HTML to text/widgets
    from gchat_integration.gchat_integration.doctype.google_chat_webhook.google_chat_webhook import convert_html_to_gchat_text
    formatted_message = convert_html_to_gchat_text(message)
    
    # Check if it's a workflow action (heuristic: if message contains "Approve" or "Reject" or if we want to force it)
    # For now, let's just create a card with the message and a link
    
    from frappe.utils import get_url_to_form
    doc_url = get_url_to_form(reference_doctype, reference_name)
    
    card = {
        "cardsV2": [
            {
                "cardId": "bot-message",
                "card": {
                    "header": {
                        "title": f"{reference_doctype}: {reference_name}",
                        "subtitle": "Notification"
                    },
                    "sections": [
                        {
                            "widgets": [
                                {
                                    "textParagraph": {
                                        "text": formatted_message
                                    }
                                },
                                {
                                    "buttonList": {
                                        "buttons": [
                                            {
                                                "text": "Open Document",
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
            }
        ]
    }
    
    # If it's a Workflow Action, we might want to add Approve/Reject buttons
    # This would require checking the context or document state
    if reference_doctype == "Workflow Action":
        # Add Approve/Reject buttons
        # Note: This requires the Bot to be able to receive the action
        buttons = card["cardsV2"][0]["card"]["sections"][0]["widgets"][1]["buttonList"]["buttons"]
        buttons.extend([
            {
                "text": "Approve",
                "onClick": {
                    "action": {
                        "function": "handle_google_chat_event", # This is internal, actual API uses actionMethodName
                        "actionMethodName": "approve_workflow",
                        "parameters": [
                            {"key": "doctype", "value": reference_doctype},
                            {"key": "docname", "value": reference_name}
                        ]
                    }
                }
            },
            {
                "text": "Reject",
                "onClick": {
                    "action": {
                        "function": "handle_google_chat_event",
                        "actionMethodName": "reject_workflow",
                        "parameters": [
                            {"key": "doctype", "value": reference_doctype},
                            {"key": "docname", "value": reference_name}
                        ]
                    }
                }
            }
        ])

    frappe.logger().info(f"Bot Message Payload: {json.dumps(card)}")
    
    # TODO: Authenticate and send to Google Chat API
    # credentials = get_service_account_credentials()
    # service = build('chat', 'v1', credentials=credentials)
    # service.spaces().messages().create(parent=space_id, body=card).execute()
    
    return "success"

