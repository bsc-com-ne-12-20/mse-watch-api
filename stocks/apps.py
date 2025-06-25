from django.apps import AppConfig
import logging
import sys
import os
from datetime import datetime

logger = logging.getLogger(__name__)

class StocksConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'stocks'

    def ready(self):
        """
        Start the background data collector when Django starts.
        This replaces the old manual cache refresh approach with automatic collection.
        """
        # Only start in the main process (avoid duplicates during development)
        # Skip if we're in a migration, test, or other management command
        if (os.environ.get('RUN_MAIN') == 'true' or 
            not any(cmd in sys.argv for cmd in ['migrate', 'makemigrations', 'test', 'shell', 'collectstatic'])):
            try:
                print(f"\n\n{'*'*80}")
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] DJANGO: Starting MSE Background Data Collector")
                
                # Import and start the new background collector
                from .background_tasks import start_background_collector
                start_background_collector()
                
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] DJANGO: [SUCCESS] Background data collector started successfully")
                print(f"{'*'*80}\n")
                logger.info("Background data collector initialized in Django startup")
                
            except Exception as e:
                print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] DJANGO ERROR: Failed to start background collector: {str(e)}")
                print(f"{'*'*80}\n")
                logger.error(f"Failed to start background collector: {str(e)}", exc_info=True)
