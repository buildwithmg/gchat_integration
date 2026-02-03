# Google Chat Integration for ERPNext

A custom Frappe app that integrates Google Chat webhooks with ERPNext notifications, enabling you to send automated notifications to Google Chat spaces.

## Features

- 🔔 **Webhook Integration**: Send ERPNext notifications to Google Chat spaces via webhooks
- 💬 **Direct Message Notifications**: Send personalized DM notifications to users based on their email addresses
- 📝 **HTML Support**: Automatically converts HTML formatting (headers, lists, bold, etc.) to Google Chat format
- 📎 **Attachment Links**: Includes links to print formats and file attachments in notifications
- 🎨 **Custom Message Examples**: Provides Google Chat-specific message formatting examples
- 🔧 **Flexible Configuration**: Hide/show document links, configure webhook per notification
- 🤖 **Chatbot Integration**: Send messages via Google Chat Bot API with interactive cards

## Installation

### Prerequisites

- Frappe/ERPNext installation
- Google Chat space with webhook configured

### Install via Bench

```bash
cd frappe-bench
bench get-app https://github.com/buildwithmg/gchat_integration.git
bench --site your-site-name install-app gchat_integration
bench --site your-site-name migrate
```

## Configuration

### 1. Create Google Chat Webhook

1. In Google Chat, open the space where you want to receive notifications
2. Click the space name → **Manage webhooks**
3. Click **Add webhook**
4. Give it a name and click **Save**
5. Copy the webhook URL

### 2. Add Webhook to ERPNext

1. Go to **Desk → GChat Integration → Google Chat Webhook**
2. Click **New**
3. Enter:
   - **Webhook Name**: A descriptive name
   - **Webhook URL**: Paste the URL from Google Chat
   - **Show Document Link**: Enable to include a button linking to the document
4. Click **Save**

### 3. Configure Notification

1. Go to **Desk → Settings → Notification**
2. Create a new Notification or edit an existing one
3. Set **Channel** to **Google Chat**
4. **Google Chat Type**: Select **Webhook**, **Chatbot**, or **Direct Message**
5. Configure based on type:
   - **Webhook**: Select the webhook you created
   - **Chatbot**: Enter the Space ID
   - **Direct Message**: Add recipients (users will receive individual DMs)
6. Configure your message with Jinja templating and HTML formatting
7. **Save** and enable the notification

### 4. Direct Message Setup (Optional)

To send direct messages to users via Google Chat:

#### Prerequisites

- Google Workspace domain
- Service Account with domain-wide delegation
- Google Chat Bot app configured

#### Setup Steps

1. **Create a Service Account**:
   - Go to [Google Cloud Console](https://console.cloud.google.com)
   - Create or select a project
   - Navigate to IAM & Admin → Service Accounts
   - Create a new service account
   - Download the JSON key file

2. **Enable Domain-Wide Delegation**:
   - Go to [Google Admin Console](https://admin.google.com)
   - Navigate to Security → Access and data control → API controls
   - Click "Manage Domain-wide Delegation"
   - Add your Service Account's Client ID
   - Grant the following scopes:
     - `https://www.googleapis.com/auth/chat.spaces`
     - `https://www.googleapis.com/auth/chat.bot`

3. **Configure Google Chat Settings**:
   - Go to **Desk → Google Chat Settings**
   - Enable **Bot Integration**
   - Paste your Service Account JSON in the **Service Account JSON** field
   - Configure your bot details
   - Save

4. **Create Direct Message Notification**:
   - Create a new Notification
   - Set Channel to **Google Chat**
   - Set Google Chat Type to **Direct Message**
   - Add recipients (users from your ERPNext system)
   - Configure your message
   - Save and test

**Important**: Recipients must have valid Google Workspace email addresses that match their ERPNext user emails.

## Message Formatting

### Supported HTML Tags

The integration automatically converts HTML to Google Chat format:

- `<h1>` to `<h6>` → Bold text with newline
- `<p>` → Paragraph with spacing
- `<ul>` and `<li>` → Bullet lists
- `<b>`, `<strong>` → **Bold**
- `<i>`, `<em>` → _Italic_
- `<s>`, `<strike>` → ~Strikethrough~

### Example Message

```html
<h3>Order Overdue</h3>

<p>Transaction {{ doc.name }} has exceeded Due Date. Please take necessary action.</p>

<!-- show last comment -->
{% if comments %}
Last comment: {{ comments[-1].comment }} by {{ comments[-1].by }}
{% endif %}

<h4>Details</h4>

<ul>
<li>Customer: {{ doc.customer }}</li>
<li>Amount: {{ doc.grand_total }}</li>
</ul>
```

## Attachments

When you enable **Attach Print** or **Attach Files** in the notification:

- **Print Format**: A link to download the PDF will be appended to the message
- **File Attachments**: Links to attached files will be included

Note: Google Chat webhooks don't support direct file uploads, so clickable links are provided instead.

## Architecture

### Key Components

- **Google Chat Webhook DocType**: Stores webhook configurations
- **Notification Extension**: Monkey patches the core Notification DocType to add Google Chat support
- **HTML Converter**: Converts HTML formatting to Google Chat text format
- **Custom Fields**: Adds `google_chat_type` and `google_chat_webhook` fields to Notification
- **Property Setters**: Hides irrelevant fields (like Recipients) when Google Chat is selected

### Files

- `gchat_integration/doctype/google_chat_webhook/` - Webhook DocType and sending logic
- `gchat_integration/notification_extension.py` - Extends Notification DocType
- `gchat_integration/install.py` - Installation hooks and field setup
- `gchat_integration/public/js/notification_custom.js` - Custom UI for Notification form
- `gchat_integration/hooks.py` - App configuration and hooks

## Troubleshooting

### Notifications Not Sending

1. Check Error Log: **Desk → Tools → Error Log**
2. Verify webhook URL is correct in Google Chat
3. Ensure notification is enabled
4. Check that the event trigger matches your action
5. Clear cache: `bench --site your-site clear-cache`

### Extension Not Loading

If the Google Chat channel option doesn't appear:

```bash
bench --site your-site migrate
bench --site your-site clear-cache
```

### Webhook URL Too Long

The app uses `Small Text` field type to support long webhook URLs (up to 64k characters).

## Development

### Running Tests

```bash
bench --site your-site run-tests --app gchat_integration
```

### Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Roadmap

- [x] Google Chat Chatbot integration (direct user messaging)
- [x] Direct Message notifications via email
- [ ] Rich card formatting options
- [ ] Interactive buttons and forms
- [ ] Thread support for related notifications
- [ ] Caching DM space IDs for performance

## License

MIT

## Credits

Developed by [buildwithmg](https://github.com/buildwithmg)

Inspired by the Slack integration in Frappe core.

## Support

For issues and questions:
- GitHub Issues: https://github.com/buildwithmg/gchat_integration/issues
- Frappe Forum: https://discuss.frappe.io/

---

**Note**: This is a custom app and is not officially supported by Frappe Technologies.
