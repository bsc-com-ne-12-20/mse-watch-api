from django.core.management.base import BaseCommand
from stocks.services.historical_service import MSEHistoricalService
from stocks.models import Company
import json

class Command(BaseCommand):
    help = 'Test the new MSE historical data scraper'

    def add_arguments(self, parser):
        parser.add_argument(
            '--symbol',
            type=str,
            default='AIRTEL',
            help='Stock symbol to test (default: AIRTEL)'
        )
        parser.add_argument(
            '--range',
            type=str,
            default='1month',
            help='Time range to test (default: 1month)'
        )

    def handle(self, *args, **options):
        symbol = options['symbol'].upper()
        time_range = options['range']
        
        self.stdout.write(f"Testing MSE scraper for {symbol} with range {time_range}")
        
        # Initialize service
        service = MSEHistoricalService()
        
        # Test the scraper
        try:
            data = service.get_historical_data(symbol, time_range)
            
            if data:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"✅ Successfully fetched data for {symbol}"
                    )
                )
                self.stdout.write(f"   Company: {data['company']['name']}")
                self.stdout.write(f"   Data points: {data['data_points']}")
                self.stdout.write(f"   Time range: {data['time_range']}")
                self.stdout.write(f"   Source: {data['source']}")
                
                # Show first few data points
                if data['stock_prices']:
                    self.stdout.write("\n   Sample data points:")
                    for i, price in enumerate(data['stock_prices'][:3]):
                        self.stdout.write(f"   {i+1}. {price['date']}: {price['price']}")
                    
                    if len(data['stock_prices']) > 3:
                        self.stdout.write(f"   ... and {len(data['stock_prices']) - 3} more")
                
                # Test saving to database
                self.stdout.write("\n📊 Testing database save...")
                saved_count = service.save_to_database(symbol, data)
                self.stdout.write(
                    self.style.SUCCESS(
                        f"✅ Saved {saved_count} records to database"
                    )
                )
                
            else:
                self.stdout.write(
                    self.style.ERROR(
                        f"❌ Failed to fetch data for {symbol}"
                    )
                )
                
                # Check if company ID mapping exists
                company_id = service.get_company_id_from_symbol(symbol)
                if not company_id:
                    self.stdout.write(
                        self.style.WARNING(
                            f"⚠️  No company ID mapping found for {symbol}. "
                            f"You need to add the mapping in the service."
                        )
                    )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(
                    f"❌ Error during testing: {str(e)}"
                )            )
        
        self.stdout.write("\n🔍 Current company ID mappings:")
        mappings = {
            'AIRTEL': 'MWAIRT001156',
            'BHL': 'MWBHL0010029',
            'FDHB': 'MWFDHB001166',
            'FMBCH': 'MWFMB0010138',
            'ICON': 'MWICON001146',
            'ILLOVO': 'MWILLV010032',
            'MPICO': 'MWMPI0010116',
            'NBM': 'MWNBM0010074',
            'NBS': 'MWNBS0010105',
            'NICO': 'MWNICO010014',
            'NITL': 'MWNITL010091',
            'OMU': 'ZAE000255360',
            'PCL': 'MWPCL0010053',
            'STANDARD': 'MWSTD0010041',
            'SUNBIRD': 'MWSTL0010085',
            'TNM': 'MWTNM0010126',
        }
        
        for sym, comp_id in mappings.items():
            self.stdout.write(f"   {sym}: {comp_id}")
        
        self.stdout.write(
            self.style.WARNING(
                "\n⚠️  Note: You may need to add more company ID mappings "
                "based on the actual MSE company IDs."
            )
        )
