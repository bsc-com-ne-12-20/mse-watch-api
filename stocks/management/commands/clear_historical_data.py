from django.core.management.base import BaseCommand
from stocks.models import HistoricalPrice
from django.core.cache import cache

class Command(BaseCommand):
    help = 'Clear all historical price data and cache'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirm deletion of all historical data',
        )

    def handle(self, *args, **options):
        if not options['confirm']:
            self.stdout.write(
                self.style.WARNING(
                    'This will delete ALL historical price data. '
                    'Use --confirm to proceed.'
                )
            )
            return

        # Clear historical price data
        count = HistoricalPrice.objects.count()
        if count > 0:
            HistoricalPrice.objects.all().delete()
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully deleted {count} historical price records'
                )
            )
        else:
            self.stdout.write('No historical price records found')

        # Clear cache
        cache.clear()
        self.stdout.write(
            self.style.SUCCESS('Successfully cleared cache')
        )

        self.stdout.write(
            self.style.SUCCESS('Historical data cleanup completed!')
        )
