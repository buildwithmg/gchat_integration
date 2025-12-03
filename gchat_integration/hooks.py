app_name = "gchat_integration"
app_title = "Gchat Integration"
app_publisher = "Frappe"
app_description = "Google Chat Webhook Integration for ERPNext"
app_email = "support@keystoneuae.com"
app_license = "mit"

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "gchat_integration",
# 		"logo": "/assets/gchat_integration/logo.png",
# 		"title": "Gchat Integration",
# 		"route": "/gchat_integration",
# 		"has_permission": "gchat_integration.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/gchat_integration/css/gchat_integration.css"
# app_include_js = "/assets/gchat_integration/js/gchat_integration.js"

# include js, css files in header of web template
# web_include_css = "/assets/gchat_integration/css/gchat_integration.css"
# web_include_js = "/assets/gchat_integration/js/gchat_integration.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "gchat_integration/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "gchat_integration/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# automatically load and sync documents of this doctype from downstream apps
# importable_doctypes = [doctype_1]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "gchat_integration.utils.jinja_methods",
# 	"filters": "gchat_integration.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "gchat_integration.install.before_install"
after_install = "gchat_integration.gchat_integration.install.after_install"

# Fixtures - Custom fields for Notification DocType
fixtures = [
	{
		"dt": "Custom Field",
		"filters": [
			[
				"name",
				"in",
				[
					"Notification-google_chat_webhook"
				]
			]
		]
	},
	{
		"dt": "Property Setter",
		"filters": [
			[
				"name",
				"in",
				[
					"Notification-channel-options"
				]
			]
		]
	}
]


# Uninstallation
# ------------

# before_uninstall = "gchat_integration.uninstall.before_uninstall"
# after_uninstall = "gchat_integration.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "gchat_integration.utils.before_app_install"
# after_app_install = "gchat_integration.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "gchat_integration.utils.before_app_uninstall"
# after_app_uninstall = "gchat_integration.utils.after_app_uninstall"

# DocType JS
# ----------
doctype_js = {
	"Notification": "public/js/notification_custom.js"
}

# Desk Notifications
# ------------------

# See frappe.core.notifications.get_notification_config

# notification_config = "gchat_integration.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"gchat_integration.tasks.all"
# 	],
# 	"daily": [
# 		"gchat_integration.tasks.daily"
# 	],
# 	"hourly": [
# 		"gchat_integration.tasks.hourly"
# 	],
# 	"weekly": [
# 		"gchat_integration.tasks.weekly"
# 	],
# 	"monthly": [
# 		"gchat_integration.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "gchat_integration.install.before_tests"

# Extend DocType Class
# ------------------------------
#
# Specify custom mixins to extend the standard doctype controller.
# extend_doctype_class = {
# 	"Task": "gchat_integration.custom.task.CustomTaskMixin"
# }

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "gchat_integration.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "gchat_integration.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["gchat_integration.utils.before_request"]
# after_request = ["gchat_integration.utils.after_request"]

# Migrate
# -------
after_migrate = "gchat_integration.gchat_integration.install.setup_notification_extension"

# App startup - Load notification extension on every request
# This ensures Google Chat functionality is available
app_startup = "gchat_integration.gchat_integration.notification_extension.extend_notification"



# Job Events
# ----------
# before_job = ["gchat_integration.utils.before_job"]
# after_job = ["gchat_integration.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"gchat_integration.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

# Translation
# ------------
# List of apps whose translatable strings should be excluded from this app's translations.
# ignore_translatable_strings_from = []

