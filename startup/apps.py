"""
Startup app for running migrations and initial data setup on app initialization.
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
        """Run migrations and populate initial data when app is ready"""
        logger.info("=" * 70)
        logger.info("STARTUP: Running database migrations...")
        logger.info("=" * 70)
        
        try:
            # Run migrations silently if they're already applied
            call_command('migrate', verbosity=2, interactive=False)
            logger.info("=" * 70)
            logger.info("STARTUP: Migrations completed successfully!")
            logger.info("=" * 70)
            
            # Populate sample doctors if database is empty
            logger.info("")
            logger.info("STARTUP: Populating sample data...")
            call_command('populate_doctors', verbosity=1, interactive=False)
            logger.info("STARTUP: Sample data populated!")
            
        except Exception as e:
            logger.error(f"STARTUP: Failed during initialization: {str(e)}")
            # Don't exit, let Django continue but log the error
            import traceback
            logger.error(traceback.format_exc())
