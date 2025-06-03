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

    def handle(self, *args, **kwargs):
        start_time = datetime.now()
        print(f"\n{'='*80}\n[{start_time.strftime('%Y-%m-%d %H:%M:%S')}] SCRAPER: Starting MSE stock data scraper\n{'='*80}")
        
        try:
            # Get the full path to the scraper script
            base_dir = Path(__file__).resolve().parent.parent.parent.parent
            scraper_path = os.path.join(base_dir, 'mse_scrapper_html.py')
            
            logger.info(f"Starting stock scraper at {datetime.now()}")
            
            # Import and run the scraper function
            sys.path.append(str(base_dir))
            from mse_scrapper_html import extract_mse_data_html, save_data, save_to_database
            
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] SCRAPER: Extracting MSE stock data...")
            df = extract_mse_data_html()
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