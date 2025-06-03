import threading
import time
import logging
import schedule
from django.core import management
from django.conf import settings
import os
from datetime import datetime

# Configure console logger
logger = logging.getLogger(__name__)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_formatter = logging.Formatter('%(asctime)s [SCHEDULER] %(message)s')
console_handler.setFormatter(console_formatter)
logger.addHandler(console_handler)

def run_scraper():
    """Run the stock scraper management command"""
    try:
        print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] SCHEDULER: Running scheduled stock scraper")
        logger.info("Running scheduled stock scraper")
        management.call_command('scrape_stocks')
    except Exception as e:
        print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] SCHEDULER ERROR: {str(e)}")
        logger.error(f"Error in scheduled scraper: {str(e)}", exc_info=True)

def schedule_scraper():
    """Schedule the stock scraper to run at specific times"""
    # Run every weekday (Monday to Friday) at specific hours
    # MSE trading hours: 09:00-11:00 (morning session), 14:00-15:00 (afternoon session)
    
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] SCHEDULER: Setting up MSE stock data collection schedule")
    
    # For development/testing: Run every 2 minutes
    # This makes it easy to see the scheduler working during development
    schedule.every(2).minutes.do(run_scraper)
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] SCHEDULER: Added development schedule - every 2 minutes")
    
    # Morning session scraping (9:00 to 11:00, every 15 minutes)
    for hour in [9, 10]:
        for minute in [0, 15, 30, 45]:
            schedule.every().monday.at(f"{hour:02d}:{minute:02d}").do(run_scraper)
            schedule.every().tuesday.at(f"{hour:02d}:{minute:02d}").do(run_scraper)
            schedule.every().wednesday.at(f"{hour:02d}:{minute:02d}").do(run_scraper)
            schedule.every().thursday.at(f"{hour:02d}:{minute:02d}").do(run_scraper)
            schedule.every().friday.at(f"{hour:02d}:{minute:02d}").do(run_scraper)
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] SCHEDULER: Added morning session schedule (9:00-11:00, every 15 min)")
    
    # Afternoon session scraping (14:00 to 15:00, every 10 minutes)
    for hour in [14]:
        for minute in [0, 10, 20, 30, 40, 50]:
            schedule.every().monday.at(f"{hour:02d}:{minute:02d}").do(run_scraper)
            schedule.every().tuesday.at(f"{hour:02d}:{minute:02d}").do(run_scraper)
            schedule.every().wednesday.at(f"{hour:02d}:{minute:02d}").do(run_scraper)
            schedule.every().thursday.at(f"{hour:02d}:{minute:02d}").do(run_scraper)
            schedule.every().friday.at(f"{hour:02d}:{minute:02d}").do(run_scraper)
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] SCHEDULER: Added afternoon session schedule (14:00-15:00, every 10 min)")
    
    # End of day capture
    schedule.every().monday.at("17:00").do(run_scraper)
    schedule.every().tuesday.at("17:00").do(run_scraper)
    schedule.every().wednesday.at("17:00").do(run_scraper)
    schedule.every().thursday.at("17:00").do(run_scraper)
    schedule.every().friday.at("17:00").do(run_scraper)
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] SCHEDULER: Added end-of-day schedule (17:00)")

def start_scheduler():
    """Start the scheduler in a background thread"""
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] SCHEDULER: Starting MSE stock price scheduler service")
    logger.info("Starting scheduler service")
    schedule_scraper()
    
    # Run immediately when starting up (optional)
    if os.environ.get('RUN_SCRAPER_ON_STARTUP', 'false').lower() == 'true':
        print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] SCHEDULER: Running initial scrape on startup")
        run_scraper()
    else:
        print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] SCHEDULER: Set RUN_SCRAPER_ON_STARTUP=true to run scraper immediately")
    
    def run_threaded():
        next_run = schedule.next_run()
        if next_run:
            print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] SCHEDULER: Next scheduled run at {next_run}")
        
        while True:
            schedule.run_pending()
            
            # Check if there's a new next run time to report
            new_next_run = schedule.next_run()
            if new_next_run and new_next_run != next_run:
                next_run = new_next_run
                print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] SCHEDULER: Next scheduled run at {next_run}")
            
            time.sleep(60)  # Check every minute
    
    # Run the scheduler in a separate thread
    thread = threading.Thread(target=run_threaded, daemon=True)
    thread.start()
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] SCHEDULER: Started successfully, running in background")
    logger.info("Scheduler started successfully")