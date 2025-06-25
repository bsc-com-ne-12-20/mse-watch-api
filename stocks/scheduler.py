import threading
import time
import logging
import schedule
import subprocess
import sys
import os
import django
from django.core import management
from django.conf import settings
from datetime import datetime
import requests
from django.core.cache import cache
from django.db import models
from typing import List, Dict

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(settings.BASE_DIR, 'scheduler.log'))
    ]
)

logger = logging.getLogger(__name__)

# Cache warming configuration
CACHE_WARM_CONFIG = {
    'enabled': True,
    'api_key': 'mse_5PFAyspVWQnz33boHidjCIiU2y6aNoEmzZteXzRV',
    'base_url': 'http://127.0.0.1:8000/api/historical',
    'priority_symbols': ['AIRTEL', 'TNM', 'NBM', 'STANDARD', 'NICO', 'FDHB'],
    'all_symbols': [
        'AIRTEL', 'BHL', 'FDHB', 'FMBCH', 'ICON', 'ILLOVO',
        'MPICO', 'NBM', 'NBS', 'NICO', 'NITL', 'OMU',
        'PCL', 'STANDARD', 'SUNBIRD', 'TNM'
    ],
    'ranges': {
        'priority': ['1day', '1month', '1year'],  # Most important
        'standard': ['1day', '1month', '3months', '6months', '1year'],  # Regular
        'full': ['1day', '1month', '3months', '6months', '1year', '2years', '5years']  # Complete
    }
}

def run_scraper(force=False):
    """Run the stock scraper management command
    
    Args:
        force (bool): Whether to force scrape even if market is closed
    """
    try:
        # Check if it's weekend (Saturday = 5, Sunday = 6)
        current_weekday = datetime.now().weekday()
        if current_weekday in [5, 6] and not force:  # Saturday or Sunday
            weekday_name = "Saturday" if current_weekday == 5 else "Sunday"
            print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] SCHEDULER: Market is closed on {weekday_name}. Stock exchanges do not operate on weekends.")
            logger.info(f"Market is closed on {weekday_name}. Skipping scheduled scrape.")
            return
        
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

def send_daily_report():
    """Execute the send_daily_report management command"""
    # Get the current weekday (0 is Monday, 6 is Sunday)
    weekday = datetime.now().weekday()
    
    # Only run on weekdays (Monday to Friday: 0-4)
    if weekday <= 4:
        logger.info("Starting daily market report email task")
        try:
            # Get the path to the current Python executable
            python_exec = sys.executable
            
            # Get the path to the project's manage.py
            manage_py = os.path.join(settings.BASE_DIR, 'manage.py')
            
            # Execute the command as a subprocess
            result = subprocess.run(
                [python_exec, manage_py, 'send_daily_report'],
                capture_output=True,
                text=True,
                check=True
            )
            
            logger.info(f"Daily report sent successfully: {result.stdout}")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Error sending daily report: {e.stderr}")
            return False
    else:
        logger.info("Skipping daily report on weekend")
        return False

def run_scheduler():
    """Run the scheduler"""
    logger.info("Starting email report scheduler")
    
    # Schedule the daily report at 6:00 PM (18:00)
    schedule.every().day.at("18:00").do(send_daily_report)
    
    logger.info("Email reports scheduled for 6:00 PM on weekdays")
    
    # Run the scheduler loop
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

def start_scheduler():
    """Start the scheduler in a background thread"""
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] SCHEDULER: Starting MSE stock price scheduler service")
    logger.info("Starting scheduler service")
    
    # Set up stock scraping schedule
    schedule_scraper()
    
    # Set up cache warming schedule
    schedule_cache_warming()
    
    # Run immediately when starting up (optional)
    if os.environ.get('RUN_SCRAPER_ON_STARTUP', 'false').lower() == 'true':
        print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] SCHEDULER: Running initial scrape on startup")
        run_scraper()
    else:
        print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] SCHEDULER: Set RUN_SCRAPER_ON_STARTUP=true to run scraper immediately")
    
    # Optionally run initial cache warming
    if os.environ.get('RUN_CACHE_WARM_ON_STARTUP', 'false').lower() == 'true':
        print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] SCHEDULER: Running initial cache warming")
        run_cache_warming('priority')
    
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

def warm_cache_for_symbol_range(symbol: str, time_range: str) -> bool:
    """Warm cache for a specific symbol and time range"""
    if not CACHE_WARM_CONFIG['enabled']:
        return True
        
    try:
        url = f"{CACHE_WARM_CONFIG['base_url']}/{symbol}/"
        params = {'range': time_range, 'refresh': 'true'}
        headers = {
            'X-API-Key': CACHE_WARM_CONFIG['api_key'],
            'Content-Type': 'application/json'
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            points = data.get('data_points', 0)
            logger.info(f"Cache warmed: {symbol} {time_range} ({points} points)")
            return True
        else:
            logger.warning(f"Cache warm failed: {symbol} {time_range} - HTTP {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"Cache warm error: {symbol} {time_range} - {str(e)}")
        return False

def run_cache_warming(strategy: str = 'priority'):
    """Run cache warming with different strategies
    
    Args:
        strategy: 'priority', 'standard', 'full', or 'intraday_only'
    """
    if not CACHE_WARM_CONFIG['enabled']:
        logger.info("Cache warming is disabled")
        return
    
    start_time = datetime.now()
    logger.info(f"Starting cache warming - strategy: {strategy}")
    
    successful = 0
    total = 0
    
    try:
        if strategy == 'intraday_only':
            # Just warm the most time-sensitive data (1day for all symbols)
            symbols = CACHE_WARM_CONFIG['all_symbols']
            ranges = ['1day']
        elif strategy == 'priority':
            # Priority symbols with important ranges
            symbols = CACHE_WARM_CONFIG['priority_symbols']
            ranges = CACHE_WARM_CONFIG['ranges']['priority']
        elif strategy == 'standard':
            # All symbols with standard ranges
            symbols = CACHE_WARM_CONFIG['all_symbols']
            ranges = CACHE_WARM_CONFIG['ranges']['standard']
        elif strategy == 'full':
            # All symbols with all ranges
            symbols = CACHE_WARM_CONFIG['all_symbols']
            ranges = CACHE_WARM_CONFIG['ranges']['full']
        else:
            logger.error(f"Unknown cache warming strategy: {strategy}")
            return
        
        # Warm cache with small delays to avoid overwhelming the server
        for symbol in symbols:
            for time_range in ranges:
                if warm_cache_for_symbol_range(symbol, time_range):
                    successful += 1
                total += 1
                
                # Small delay to be nice to the server
                time.sleep(0.2)
        
        duration = datetime.now() - start_time
        success_rate = (successful / total * 100) if total > 0 else 0
        
        logger.info(f"Cache warming completed: {successful}/{total} ({success_rate:.1f}%) in {duration}")
        
    except Exception as e:
        logger.error(f"Cache warming failed: {str(e)}")

def schedule_cache_warming():
    """Schedule cache warming at optimal times"""
    logger.info("Setting up cache warming schedule")
    
    # Strategy 1: Intraday cache warming every hour during market hours
    # This keeps the most time-sensitive data fresh
    weekdays = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']
    market_hours = [9, 10, 11, 12, 13, 14, 15, 16]  # 9 AM to 4 PM
    
    for day in weekdays:
        for hour in market_hours:
            time_str = f"{hour:02d}:00"
            getattr(schedule.every(), day).at(time_str).do(run_cache_warming, 'intraday_only')
    
    logger.info("Scheduled intraday cache warming (1day range) every hour during market hours")
    
    # Strategy 2: Priority cache warming twice daily
    # Morning: Before market opens
    for day in weekdays:
        getattr(schedule.every(), day).at("08:30").do(run_cache_warming, 'priority')
    
    # Evening: After market closes
    for day in weekdays:
        getattr(schedule.every(), day).at("17:30").do(run_cache_warming, 'priority')
    
    logger.info("Scheduled priority cache warming at 8:30 AM and 5:30 PM")
    
    # Strategy 3: Full cache warming once daily (early morning)
    # This ensures all data is fresh for the day
    for day in weekdays:
        getattr(schedule.every(), day).at("06:00").do(run_cache_warming, 'standard')
    
    logger.info("Scheduled standard cache warming at 6:00 AM daily")
    
    # Strategy 4: Weekend maintenance (light warming)
    schedule.every().saturday.at("10:00").do(run_cache_warming, 'priority')
    schedule.every().sunday.at("10:00").do(run_cache_warming, 'priority')
    
    logger.info("Scheduled weekend cache maintenance")

if __name__ == "__main__":
    # Set up Django environment
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    django.setup()
    
    # Run the scheduler
    run_scheduler()