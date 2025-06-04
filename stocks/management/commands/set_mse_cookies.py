from django.core.management.base import BaseCommand
from stocks.services.historical_service import MSEHistoricalService
import pickle
import os
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Set cookies for MSE website authentication'
    
    def add_arguments(self, parser):
        parser.add_argument(
            'cookie_string',
            type=str,
            help='Cookie string from browser (copy from Developer Tools)'
        )
        parser.add_argument(
            '--test',
            action='store_true',
            help='Test the cookies by fetching TNM 1-month data'
        )
    
    def handle(self, *args, **options):
        cookie_string = options['cookie_string']
        test = options.get('test', False)
        
        if not cookie_string:
            self.stdout.write(self.style.ERROR("Cookie string is required"))
            return
        
        # Create service and set cookies
        service = MSEHistoricalService()
        success = service.set_manual_cookies(cookie_string)
        
        if not success:
            self.stdout.write(self.style.ERROR("Failed to set cookies"))
            return
        
        # Save cookies to file for reuse
        cookie_file = os.path.join(Path.home(), '.mse_cookies')
        try:
            with open(cookie_file, 'wb') as f:
                pickle.dump(service.session.cookies, f)
            self.stdout.write(self.style.SUCCESS(f"Cookies saved to {cookie_file}"))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"Could not save cookies: {str(e)}"))
        
        # Test the cookies if requested
        if test:
            self.stdout.write("Testing cookies by fetching TNM 1-month data...")
            data = service.get_historical_data('TNM', '1month')
            
            if data and 'stock_prices' in data and data['stock_prices']:
                self.stdout.write(self.style.SUCCESS(
                    f"Successfully fetched {len(data['stock_prices'])} data points for TNM"
                ))
            else:
                self.stdout.write(self.style.ERROR("Failed to fetch data, cookies may be invalid"))