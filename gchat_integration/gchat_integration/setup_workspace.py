import frappe

def setup_integrations_workspace():
    try:
        workspace = frappe.get_doc("Workspace", "Integrations")
        
        # Find existing link
        existing_link = None
        existing_idx = -1
        for idx, link in enumerate(workspace.links):
            if link.label == "Google Chat Webhook":
                existing_link = link
                existing_idx = idx
                break

        # Find Slack Webhook URL position
        slack_idx = -1
        for idx, link in enumerate(workspace.links):
            if link.label == "Slack Webhook URL":
                slack_idx = idx
                break
        
        if slack_idx == -1:
            # Fallback if Slack link not found
            if not existing_link:
                new_link = frappe.new_doc("Workspace Link")
                new_link.label = "Google Chat Webhook"
                new_link.type = "Link"
                new_link.link_type = "DocType"
                new_link.link_to = "Google Chat Webhook"
                new_link.is_query_report = 0
                workspace.append("links", new_link)
                workspace.save()
            return

        # If link exists
        if existing_link:
            # Check if it's already in the correct position (immediately after Slack)
            # Note: if existing_idx > slack_idx, the position is existing_idx
            # if existing_idx < slack_idx, the slack_idx will shift down by 1 when we remove existing
            
            # Let's just remove and re-insert to be safe and simple
            if existing_idx != slack_idx + 1:
                workspace.links.pop(existing_idx)
                
                # Re-find slack_idx because list changed
                for idx, link in enumerate(workspace.links):
                    if link.label == "Slack Webhook URL":
                        slack_idx = idx
                        break
                
                workspace.links.insert(slack_idx + 1, existing_link)
                
                # Update idx
                for i, link in enumerate(workspace.links):
                    link.idx = i + 1
                    
                workspace.save()
                frappe.db.commit()
            
        else:
            # Create new link
            new_link = frappe.new_doc("Workspace Link")
            new_link.label = "Google Chat Webhook"
            new_link.type = "Link"
            new_link.link_type = "DocType"
            new_link.link_to = "Google Chat Webhook"
            new_link.is_query_report = 0
            
            workspace.links.insert(slack_idx + 1, new_link)
            
            # Update idx
            for i, link in enumerate(workspace.links):
                link.idx = i + 1
                
            workspace.save()
            frappe.db.commit()
            
    except frappe.DoesNotExistError:
        pass
    except Exception as e:
        frappe.log_error(f"Failed to setup integrations workspace: {str(e)}")
