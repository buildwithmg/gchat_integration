/*
* Custom JS for Notification DocType to support Google Chat integration
*/

// Extend setup_example_message to handle Google Chat
if (frappe.notification) {
    const original_setup_example_message = frappe.notification.setup_example_message;

    frappe.notification.setup_example_message = function (frm) {
        if (frm.doc.channel === "Google Chat") {
            let template = `<h5>Message Example</h5>
<pre>*Order Overdue*

Transaction {{ doc.name }} has exceeded Due Date. Please take necessary action.

<!-- show last comment -->
{% if comments %}
Last comment: {{ comments[-1].comment }} by {{ comments[-1].by }}
{% endif %}

*Details*

• Customer: {{ doc.customer }}
• Amount: {{ doc.grand_total }}
</pre>
<p class="text-muted small">
    Note: Google Chat supports simple formatting like *bold*, _italics_, and ~strikethrough~.
    HTML tags like &lt;h3&gt;, &lt;ul&gt;, &lt;li&gt; are automatically converted.
</p>`;

            const message_examples_field = frm.get_field("message_examples");
            if (message_examples_field) {
                message_examples_field.html(template);
            }
        } else {
            // Call original for other channels
            if (original_setup_example_message) {
                original_setup_example_message(frm);
            }
        }
    };
}
