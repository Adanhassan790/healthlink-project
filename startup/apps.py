"""
Startup app for application bootstrapping.

This app should stay lightweight. Database migrations and sample-data loading
must be run explicitly during deployment, not inside AppConfig.ready().
"""
from django.apps import AppConfig
import logging

logger = logging.getLogger(__name__)

def create_admin_user_if_not_exists():
    """Create default admin superuser if it doesn't exist"""
    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@healthlink.com',
                password='AdminPass123!'
            )
            logger.info("STARTUP: Created default admin superuser (admin/AdminPass123!)")
        else:
            logger.info("STARTUP: Admin user already exists")
    except Exception as e:
        logger.error(f"STARTUP: Error creating admin user: {str(e)}")

class StartupAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'startup'
    verbose_name = "Application Startup"

    def ready(self):
        """Keep app startup lightweight to avoid blocking the worker."""
        logger.info("STARTUP: Startup app ready; database setup is handled externally.")
