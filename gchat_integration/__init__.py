__version__ = "0.0.1"

# Initialize notification extension
try:
	from gchat_integration.gchat_integration.notification_extension import extend_notification
	extend_notification()
except Exception:
	# Fails during installation/migration when dependencies aren't ready
	pass
