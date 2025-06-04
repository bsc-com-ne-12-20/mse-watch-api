from django.core.management.base import BaseCommand
import os
import sys
import subprocess
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Start the scheduler for recurring tasks like daily email reports'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--daemon',
            action='store_true',
            help='Run the scheduler as a daemon process in the background',
        )
    
    def handle(self, *args, **options):
        scheduler_script = os.path.join(settings.BASE_DIR, 'stocks', 'scheduler.py')
        python_exec = sys.executable
        
        if options['daemon']:
            self.stdout.write("Starting scheduler as daemon process...")
            
            # Start the scheduler as a background process
            if os.name == 'nt':  # Windows
                # On Windows, we use the start command
                subprocess.Popen(
                    f'start /B "" {python_exec} {scheduler_script} > {os.path.join(settings.BASE_DIR, "scheduler_output.log")} 2>&1',
                    shell=True
                )
            else:  # Unix/Linux
                # On Unix-like systems, we use nohup
                subprocess.Popen(
                    f'nohup {python_exec} {scheduler_script} > {os.path.join(settings.BASE_DIR, "scheduler_output.log")} 2>&1 &',
                    shell=True
                )
                
            self.stdout.write(self.style.SUCCESS(
                f"Scheduler started in background. Check logs at {os.path.join(settings.BASE_DIR, 'scheduler_output.log')}"
            ))
        else:
            self.stdout.write("Starting scheduler in foreground...")
            
            # Run the scheduler in the foreground
            try:
                # Import and run the scheduler directly
                from stocks.scheduler import run_scheduler
                run_scheduler()
            except KeyboardInterrupt:
                self.stdout.write(self.style.WARNING("Scheduler stopped by user"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Scheduler error: {str(e)}"))