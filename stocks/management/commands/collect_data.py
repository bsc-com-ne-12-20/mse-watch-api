from django.core.management.base import BaseCommand
from stocks.background_tasks import BackgroundDataCollector
from datetime import datetime

class Command(BaseCommand):
    help = 'Manually trigger data collection tasks'

    def add_arguments(self, parser):
        parser.add_argument(
            '--intraday',
            action='store_true',
            help='Collect intraday (current stock prices) data',
        )
        parser.add_argument(
            '--historical',
            action='store_true',
            help='Collect historical data for all priority symbols',
        )
        parser.add_argument(
            '--maintenance',
            action='store_true',
            help='Run daily maintenance tasks',
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Run all data collection tasks',
        )

    def handle(self, *args, **options):
        collector = BackgroundDataCollector()
        
        self.stdout.write(f"🚀 Manual Data Collection - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.stdout.write("=" * 60)
        
        if options['all'] or options['intraday']:
            self.stdout.write("📊 Collecting intraday data...")
            collector.collect_intraday_data()
            self.stdout.write(self.style.SUCCESS("✅ Intraday data collection completed"))
        
        if options['all'] or options['historical']:
            self.stdout.write("📈 Collecting historical data...")
            collector.collect_historical_data()
            self.stdout.write(self.style.SUCCESS("✅ Historical data collection completed"))
        
        if options['all'] or options['maintenance']:
            self.stdout.write("🔧 Running maintenance tasks...")
            collector.daily_maintenance()
            self.stdout.write(self.style.SUCCESS("✅ Maintenance tasks completed"))
        
        if not any([options['intraday'], options['historical'], options['maintenance'], options['all']]):
            self.stdout.write(self.style.ERROR("❌ Please specify what to collect:"))
            self.stdout.write("   --intraday     Collect current stock prices")
            self.stdout.write("   --historical   Collect historical data")
            self.stdout.write("   --maintenance  Run maintenance tasks")
            self.stdout.write("   --all          Run everything")
            self.stdout.write("")
            self.stdout.write("Example: python manage.py collect_data --intraday")
        
        self.stdout.write("=" * 60)
