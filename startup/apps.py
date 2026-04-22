"""
Startup app for running migrations on app initialization.
This ensures migrations run whenever Django starts, regardless of entry point.
"""
from django.apps import AppConfig
from django.core.management import call_command
import logging

logger = logging.getLogger(__name__)

class StartupAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'startup'
    verbose_name = "Application Startup"

    def ready(self):
        """Run migrations when app is ready"""
        logger.info("=" * 70)
        logger.info("STARTUP: Running database migrations...")
        logger.info("=" * 70)
        
        try:
            # Run migrations silently if they're already applied
            call_command('migrate', verbosity=2, interactive=False)
            logger.info("=" * 70)
            logger.info("STARTUP: Migrations completed successfully!")
            logger.info("=" * 70)
        except Exception as e:
            logger.error(f"STARTUP: Failed to run migrations: {str(e)}")
            # Don't exit, let Django continue but at least we logged the error
            import traceback
            logger.error(traceback.format_exc())
