from django.apps import AppConfig


class NotificationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'notifications'
    def ready(self):
        # Import signal registrations
        try:
            from . import signals  # noqa: F401
        except Exception:
            # Avoid crashing app import if signals have issues; log in runtime
            import logging
            logging.getLogger(__name__).exception('Failed to import notifications.signals')
