"""
Startup app for running migrations and initial data setup on app initialization.
This ensures migrations run whenever Django starts, regardless of entry point.
"""
from django.apps import AppConfig
from django.core.management import call_command
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
            
            # Create admin user
            logger.info("")
            logger.info("STARTUP: Creating admin user if needed...")
            create_admin_user_if_not_exists()
            
            # Populate sample doctors if database is empty
            logger.info("STARTUP: Populating sample data...")
            call_command('populate_doctors', verbosity=1)
            logger.info("STARTUP: Sample data populated!")
            
        except Exception as e:
            logger.error(f"STARTUP: Failed during initialization: {str(e)}")
            # Don't exit, let Django continue but log the error
            import traceback
            logger.error(traceback.format_exc())
