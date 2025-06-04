from django.core.management.base import BaseCommand
from stocks.models import Company
from stocks.services.historical_service import MSEHistoricalService
import time
import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Fetch historical stock price data from MSE API'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--symbol',
            type=str,
            help='Only fetch data for a specific symbol'
        )
        parser.add_argument(
            '--range',
            type=str,
            choices=['1month', '3months', '6months', '1year', 'ytd', '2years', '3years', '5years', 'all'],
            default='1month',
            help='Time range to fetch (default: 1month)'
        )
        parser.add_argument(
            '--cookie',
            type=str,
            help='Cookie string to use for authentication'
        )
    
    def handle(self, *args, **options):
        symbol = options.get('symbol')
        time_range = options.get('range')
        cookie_string = options.get('cookie')
        
        self.stdout.write(f"Starting historical data collection")
        
        # Initialize service
        service = MSEHistoricalService()
        
        # Handle cookies/authentication
        if cookie_string:
            self.stdout.write("Using provided cookie string")
            service.set_manual_cookies(cookie_string)
        elif not service.authenticated:
            cookie_file = os.path.join(Path.home(), '.mse_cookies')
            if not os.path.exists(cookie_file):
                self.stdout.write(self.style.ERROR(
                    f"No cookies available. Please run 'python manage.py set_mse_cookies \"cookie_string\"' first"
                ))
                return
        
        # Test authentication
        test_data = service.get_historical_data('TNM', '1month')
        if not test_data:
            self.stdout.write(self.style.ERROR(
                "Authentication failed. Please update cookies with 'python manage.py set_mse_cookies'"
            ))
            return
        
        # Get companies to process
        if symbol:
            companies = Company.objects.filter(symbol__iexact=symbol)
            if not companies.exists():
                self.stdout.write(self.style.ERROR(f"Company with symbol {symbol} not found"))
                return
        else:
            companies = Company.objects.all()
        
        self.stdout.write(f"Processing {companies.count()} companies")
        
        # Determine which ranges to fetch
        ranges_to_fetch = []
        if time_range == 'all':
            ranges_to_fetch = service.VALID_RANGES
        else:
            ranges_to_fetch = [time_range]
        
        # Process each company
        total_processed = 0
        total_saved = 0
        
        for company in companies:
            self.stdout.write(f"Processing {company.symbol}...")
            
            for range_code in ranges_to_fetch:
                try:
                    self.stdout.write(f"  Fetching {range_code} data...")
                    historical_data = service.get_historical_data(company.symbol, range_code)
                    
                    if not historical_data:
                        self.stdout.write(self.style.WARNING(f"  No data returned for {range_code}"))
                        continue
                    
                    # Save to database
                    saved = service.save_to_database(company.symbol, historical_data)
                    self.stdout.write(self.style.SUCCESS(f"  Saved {saved} data points for {range_code}"))
                    
                    total_processed += 1
                    total_saved += saved
                    
                    # Pause to avoid overwhelming the API
                    time.sleep(1)
                    
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"  Error processing {range_code}: {str(e)}"))
        
        self.stdout.write(self.style.SUCCESS(
            f"Complete! Processed {total_processed} requests and saved {total_saved} data points"
        ))