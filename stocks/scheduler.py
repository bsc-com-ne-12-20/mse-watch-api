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

def run_scraper(force=False):
    """Run the stock scraper management command
    
    Args:
        force (bool): Whether to force scrape even if market is closed
    """
    try:
        # Check if it's outside market hours
        current_time = datetime.now()
        current_hour = current_time.hour
        current_minute = current_time.minute
        current_time_value = current_hour * 60 + current_minute  # Time in minutes since midnight
        
        # MSE market schedule (in minutes since midnight)
        market_start = 9 * 60  # 09:00 (Pre-Open)
        market_end = 17 * 60   # 17:00 (End of Post Close)
        
        # Check if current time is outside market hours
        is_outside_market_hours = current_time_value < market_start or current_time_value > market_end
        
        if is_outside_market_hours and not force:
            print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] SCHEDULER: Market is outside operating hours (current time: {current_time.strftime('%H:%M')}). Skipping scheduled scrape.")
            logger.info(f"Market is outside operating hours ({current_time.strftime('%H:%M')}). Skipping scheduled scrape.")
            return
            
        print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] SCHEDULER: Running scheduled stock scraper")
        logger.info("Running scheduled stock scraper")
        
        # Pass force=True for the end-of-day scrape at 17:00
        if force:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] SCHEDULER: Forcing scrape (end-of-day collection)")
            management.call_command('scrape_stocks', force_scrape=True)
        else:
            management.call_command('scrape_stocks')
    except Exception as e:
        print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] SCHEDULER ERROR: {str(e)}")
        logger.error(f"Error in scheduled scraper: {str(e)}", exc_info=True)

def schedule_scraper():
    """Schedule the stock scraper to run at specific times"""
    # Run every weekday (Monday to Friday) according to MSE market schedule:
    # Pre-Open: 09:00-09:30, Open: 09:30-14:30, Close: 14:30-15:00, Post Close: 15:00-17:00
    
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] SCHEDULER: Setting up MSE stock data collection schedule")
    
    # For development/testing: Run every 5 minutes during working hours
    # This makes it easy to see the scheduler working during development
    schedule.every(5).minutes.do(run_scraper)
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] SCHEDULER: Added development schedule - every 5 minutes between 9:00-17:00")
    
    # Important timestamps for market session changes - scrape at these times
    market_session_times = [
        "09:00",  # Start of Pre-Open
        "09:30",  # Start of Open
        "14:30",  # Start of Close
        "15:00",  # Start of Post Close
    ]
    
    weekdays = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']
    
    # Schedule scrapes at exact market session transitions
    for day in weekdays:
        for time_str in market_session_times:
            getattr(schedule.every(), day).at(time_str).do(run_scraper, force=True)
    
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] SCHEDULER: Added critical market transition points schedule")
    
    # Pre-Open session - Frequent scraping (every 5 minutes)
    for minute in [5, 10, 15, 20, 25]:
        hour = 9
        for day in weekdays:
            getattr(schedule.every(), day).at(f"09:{minute:02d}").do(run_scraper)
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] SCHEDULER: Added Pre-Open session schedule (09:00-09:30, every 5 min)")
    
    # Regular Open session - Less frequent scraping (every 15 minutes)
    for hour in range(9, 15):  # 9 to 14
        if hour == 9:
            # For 9, only do 45 minute mark (9:30 is already covered above)
            minutes = [45]
        elif hour == 14:
            # For 14, only do 00 and 15 (14:30 is already covered above)
            minutes = [0, 15]
        else:
            # For 10-13, do every 15 minutes
            minutes = [0, 15, 30, 45]
            
        for minute in minutes:
            for day in weekdays:
                getattr(schedule.every(), day).at(f"{hour:02d}:{minute:02d}").do(run_scraper)
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] SCHEDULER: Added Open session schedule (09:30-14:30, every 15 min)")
    
    # Close session - More frequent scraping (every 5 minutes)
    for minute in [35, 40, 45, 50, 55]:
        for day in weekdays:
            getattr(schedule.every(), day).at(f"14:{minute:02d}").do(run_scraper)
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] SCHEDULER: Added Close session schedule (14:30-15:00, every 5 min)")    # Post Close session - Less frequent scraping (every 30 minutes)
    post_close_times = ["15:30", "16:00", "16:30"]
    for time_str in post_close_times:
        for day in weekdays:
            getattr(schedule.every(), day).at(time_str).do(run_scraper)
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] SCHEDULER: Added Post-Close session schedule (15:00-17:00, every 30 min)")
    
    # End of market day capture - using force=True to ensure it runs
    for day in weekdays:
        getattr(schedule.every(), day).at("17:00").do(run_scraper, force=True)
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