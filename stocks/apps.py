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
        Start the scheduler when Django starts.
        Note: This might run twice in development with auto-reloader.
        """
        # Only start the scheduler in the main process (not during Django auto-reload)
        if not any('runserver' in arg for arg in sys.argv) or 'RUN_MAIN' in os.environ:
            try:
                print(f"\n\n{'*'*80}")
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] DJANGO: Starting MSE Stock Price Scheduler")
                from .scheduler import start_scheduler
                start_scheduler()
                print(f"{'*'*80}\n")
                logger.info("Scheduler initialized in Django startup")
            except Exception as e:
                print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] DJANGO ERROR: Failed to start scheduler: {str(e)}")
                print(f"{'*'*80}\n")
                logger.error(f"Failed to start scheduler: {str(e)}", exc_info=True)
