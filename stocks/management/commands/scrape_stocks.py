import logging
from django.core.management.base import BaseCommand
import sys
import os
from pathlib import Path
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Scrape stock data from MSE website and save to database'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--force-scrape',
            action='store_true',
            help='Force scrape even if market is closed (17:00 or later)',
        )

    def handle(self, *args, **kwargs):
        start_time = datetime.now()
        force_scrape = kwargs.get('force_scrape', False)
        
        # Check current market session
        current_time = datetime.now()
        current_hour = current_time.hour
        current_minute = current_time.minute
        current_time_value = current_hour * 60 + current_minute
        
        # Determine market session based on time
        market_session = "Outside Market Hours"
        if 9*60 <= current_time_value < 9*60+30:  # 9:00 - 9:30
            market_session = "Pre-Open"
        elif 9*60+30 <= current_time_value < 14*60+30:  # 9:30 - 14:30
            market_session = "Open"
        elif 14*60+30 <= current_time_value < 15*60:  # 14:30 - 15:00
            market_session = "Close"
        elif 15*60 <= current_time_value <= 17*60:  # 15:00 - 17:00
            market_session = "Post Close"
          # Check if outside market hours (before 9:00 or after 17:00)
        if (current_time_value < 9*60 or current_time_value > 17*60) and not force_scrape:
            self.stdout.write(self.style.WARNING(f'Market is outside operating hours (current time: {datetime.now().strftime("%H:%M")}, session: {market_session}). Use --force-scrape to override.'))
            return
            
        print(f"\n{'='*80}\n[{start_time.strftime('%Y-%m-%d %H:%M:%S')}] SCRAPER: Starting MSE stock data scraper" + 
              (" (FORCED)" if force_scrape else "") + f" - Market Session: {market_session}\n{'='*80}")
        
        try:
            # Get the full path to the scraper script
            base_dir = Path(__file__).resolve().parent.parent.parent.parent
            scraper_path = os.path.join(base_dir, 'mse_scrapper_html.py')
            
            logger.info(f"Starting stock scraper at {datetime.now()}" + (" (forced)" if force_scrape else ""))
            
            # Import and run the scraper function
            sys.path.append(str(base_dir))
            from mse_scrapper_html import extract_mse_data_html, save_data, save_to_database
            
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] SCRAPER: Extracting MSE stock data...")
            df = extract_mse_data_html(force_scrape=force_scrape)
            if df is not None:
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] SCRAPER: Successfully extracted data for {len(df)} stocks")
                logger.info(f"Successfully extracted data for {len(df)} stocks")
                
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] SCRAPER: Saving data to CSV...")
                save_data(df)  # Save to CSV
                
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] SCRAPER: Saving data to database...")
                saved_count = save_to_database(df)  # Save to database
                
                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()
                
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] SCRAPER: Saved {saved_count} stock records to database")
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] SCRAPER: Completed in {duration:.2f} seconds")
                print(f"{'='*80}")
                
                logger.info(f"Saved {saved_count} stock records to database")
                self.stdout.write(self.style.SUCCESS(f'Successfully scraped and saved {saved_count} stock records'))
            else:
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] SCRAPER ERROR: Failed to extract data")
                print(f"{'='*80}")
                logger.error("Failed to extract data")
                self.stdout.write(self.style.ERROR('Failed to extract data'))
        
        except Exception as e:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] SCRAPER ERROR: {str(e)}")
            print(f"{'='*80}")
            logger.error(f"Error running stock scraper: {str(e)}", exc_info=True)
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))