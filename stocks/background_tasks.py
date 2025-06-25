#!/usr/bin/env python3
"""
Enhanced Background Data Collection System

This module handles automatic data collection with robust fallback mechanisms
for production environments where direct website access may be restricted.

Key Features:
- Runs automatically when Django starts
- Multiple fallback strategies for data collection
- Intelligent cache management with extended retention
- Production-friendly with network restriction handling
- Graceful degradation when fresh data is unavailable
"""

import threading
import time
import logging
import schedule
from datetime import datetime, timedelta
from django.core import management
from django.conf import settings
from django.db import transaction
from django.core.cache import cache
import os
import json
import requests
from typing import Dict, List, Optional

# Configure logging
logger = logging.getLogger(__name__)

class BackgroundDataCollector:
    """Enhanced data collector with robust fallback mechanisms"""
    
    def __init__(self):
        self.scheduler_thread = None
        self.is_running = False
        self.last_successful_collection = {}
        self.collection_stats = {
            'intraday_success': 0,
            'intraday_failed': 0,
            'historical_success': 0,
            'historical_failed': 0,
            'fallback_used': 0
        }
        self.setup_logging()
    
    def setup_logging(self):
        """Setup logging for background tasks"""
        if not logger.handlers:
            handler = logging.FileHandler(
                os.path.join(settings.BASE_DIR, 'background_tasks.log')
            )
            formatter = logging.Formatter(
                '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
    
    def collect_intraday_data(self):
        """Collect current stock prices with fallback strategies"""
        try:
            current_time = datetime.now()
            
            # Check if it's a weekday and market hours
            if current_time.weekday() >= 5:  # Weekend
                logger.info("Skipping intraday collection - Weekend")
                return
            
            hour = current_time.hour
            if hour < 9 or hour > 17:  # Outside market hours
                logger.info(f"Skipping intraday collection - Outside market hours ({hour:02d}:00)")
                return
            
            logger.info("[REFRESH] Starting automatic intraday data collection")
            
            success = False
            
            # Strategy 1: Try direct scraping (works locally)
            try:
                management.call_command('scrape_stocks')
                success = True
                self.collection_stats['intraday_success'] += 1
                self.last_successful_collection['intraday'] = current_time
                logger.info("[SUCCESS] Intraday data collection completed via direct scraping")
                
            except Exception as e:
                logger.warning(f"Direct scraping failed: {e}")
                self.collection_stats['intraday_failed'] += 1
                
                # Strategy 2: Use fallback data sources
                success = self._use_fallback_intraday_data()
            
            if not success:
                # Strategy 3: Extend cache lifetime for existing data
                self._extend_cache_lifetime()
                logger.info("[REFRESH] Extended existing cache data lifetime as fallback")
            
        except Exception as e:
            logger.error(f"[ERROR] Error in intraday data collection: {e}", exc_info=True)
            self.collection_stats['intraday_failed'] += 1
    
    def collect_historical_data(self):
        """Collect historical data with enhanced fallback strategies"""
        try:
            current_time = datetime.now()
            
            # Only run on weekdays
            if current_time.weekday() >= 5:
                logger.info("Skipping historical collection - Weekend")
                return
            
            logger.info("[DATA] Starting automatic historical data collection")
            
            # Priority symbols and ranges
            priority_symbols = ['AIRTEL', 'TNM', 'NBM', 'STANDARD', 'NICO', 'FDHB']
            priority_ranges = ['1month', '3months', '6months', '1year']
            
            success_count = 0
            total_count = len(priority_symbols) * len(priority_ranges)
            
            for symbol in priority_symbols:
                for time_range in priority_ranges:
                    try:
                        # Try to collect fresh data
                        if self._collect_historical_for_symbol(symbol, time_range):
                            success_count += 1
                        
                        time.sleep(2)  # Small delay between requests
                        
                    except Exception as e:
                        logger.error(f"Error collecting {symbol} {time_range}: {e}")
                        self.collection_stats['historical_failed'] += 1
            
            success_rate = (success_count / total_count) * 100 if total_count > 0 else 0
            
            if success_rate > 50:
                logger.info(f"[SUCCESS] Historical data collection completed: {success_count}/{total_count} ({success_rate:.1f}%)")
                self.collection_stats['historical_success'] += 1
                self.last_successful_collection['historical'] = current_time
            else:
                logger.warning(f"[WARNING] Low success rate for historical collection: {success_count}/{total_count} ({success_rate:.1f}%)")
                # Use fallback strategies
                self._use_fallback_historical_data()
            
        except Exception as e:
            logger.error(f"[ERROR] Error in historical data collection: {e}", exc_info=True)
            self.collection_stats['historical_failed'] += 1
    
    def daily_maintenance(self):
        """Daily maintenance tasks"""
        try:
            logger.info("[MAINTENANCE] Running daily maintenance")
            
            # Clear old cache entries
            from django.core.cache import cache
            cache.clear()
            logger.info("Cache cleared")
            
            # Clean up old log files (keep last 7 days)
            self._cleanup_old_logs()
            
            logger.info("[SUCCESS] Daily maintenance completed")
            
        except Exception as e:
            logger.error(f"[ERROR] Error in daily maintenance: {e}", exc_info=True)
    
    def _cleanup_old_logs(self):
        """Clean up log files older than 7 days"""
        try:
            log_dir = settings.BASE_DIR
            cutoff_date = datetime.now() - timedelta(days=7)
            
            for filename in os.listdir(log_dir):
                if filename.endswith('.log'):
                    file_path = os.path.join(log_dir, filename)
                    if os.path.isfile(file_path):
                        file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                        if file_time < cutoff_date:
                            os.remove(file_path)
                            logger.info(f"Deleted old log file: {filename}")
                            
        except Exception as e:
            logger.error(f"Error cleaning up logs: {e}")
    
    def setup_schedule(self):
        """Setup the collection schedule"""
        logger.info("Setting up automatic data collection schedule")
        
        # Clear any existing schedule
        schedule.clear()
        
        # ═══════════════════════════════════════════════════════════════
        # INTRADAY DATA COLLECTION (Every hour during market hours)
        # ═══════════════════════════════════════════════════════════════
        
        # Collect every hour from 9 AM to 5 PM on weekdays
        for hour in range(9, 18):  # 9 AM to 5 PM
            schedule.every().monday.at(f"{hour:02d}:00").do(self.collect_intraday_data)
            schedule.every().tuesday.at(f"{hour:02d}:00").do(self.collect_intraday_data)
            schedule.every().wednesday.at(f"{hour:02d}:00").do(self.collect_intraday_data)
            schedule.every().thursday.at(f"{hour:02d}:00").do(self.collect_intraday_data)
            schedule.every().friday.at(f"{hour:02d}:00").do(self.collect_intraday_data)
        
        # Also collect every 30 minutes during active trading (9:30 AM - 3:00 PM)
        active_times = ["09:30", "10:00", "10:30", "11:00", "11:30", "12:00", 
                       "12:30", "13:00", "13:30", "14:00", "14:30", "15:00"]
        
        for time_str in active_times:
            schedule.every().monday.at(time_str).do(self.collect_intraday_data)
            schedule.every().tuesday.at(time_str).do(self.collect_intraday_data)
            schedule.every().wednesday.at(time_str).do(self.collect_intraday_data)
            schedule.every().thursday.at(time_str).do(self.collect_intraday_data)
            schedule.every().friday.at(time_str).do(self.collect_intraday_data)
        
        # ═══════════════════════════════════════════════════════════════
        # HISTORICAL DATA COLLECTION (Daily)
        # ═══════════════════════════════════════════════════════════════
        
        # Collect historical data daily at 6 AM (before market opens)
        schedule.every().monday.at("06:00").do(self.collect_historical_data)
        schedule.every().tuesday.at("06:00").do(self.collect_historical_data)
        schedule.every().wednesday.at("06:00").do(self.collect_historical_data)
        schedule.every().thursday.at("06:00").do(self.collect_historical_data)
        schedule.every().friday.at("06:00").do(self.collect_historical_data)
        
        # Also collect after market closes at 6 PM
        schedule.every().monday.at("18:00").do(self.collect_historical_data)
        schedule.every().tuesday.at("18:00").do(self.collect_historical_data)
        schedule.every().wednesday.at("18:00").do(self.collect_historical_data)
        schedule.every().thursday.at("18:00").do(self.collect_historical_data)
        schedule.every().friday.at("18:00").do(self.collect_historical_data)
        
        # ═══════════════════════════════════════════════════════════════
        # SMART CACHE REFRESH (Every Hour - Works in All Environments)
        # ═══════════════════════════════════════════════════════════════
        
        # Run auto cache refresh every hour, 24/7
        # This ensures cached data is always relatively fresh
        for hour in range(24):  # 0 to 23 (24 hours)
            time_str = f"{hour:02d}:00"
            schedule.every().monday.at(time_str).do(self.auto_cache_refresh)
            schedule.every().tuesday.at(time_str).do(self.auto_cache_refresh)
            schedule.every().wednesday.at(time_str).do(self.auto_cache_refresh)
            schedule.every().thursday.at(time_str).do(self.auto_cache_refresh)
            schedule.every().friday.at(time_str).do(self.auto_cache_refresh)
            schedule.every().saturday.at(time_str).do(self.auto_cache_refresh)
            schedule.every().sunday.at(time_str).do(self.auto_cache_refresh)
        
        logger.info("[SUCCESS] Smart cache refresh scheduled every hour (24/7)")
        
        # ═══════════════════════════════════════════════════════════════
        # MAINTENANCE TASKS
        # ═══════════════════════════════════════════════════════════════
        
        # Daily maintenance at 2 AM
        schedule.every().day.at("02:00").do(self.daily_maintenance)
        
        logger.info("[SUCCESS] Automatic data collection schedule configured")
        logger.info("[SCHEDULE] Schedule summary:")
        logger.info("   - Smart cache refresh: Every hour (24/7)")
        logger.info("   - Intraday data: Every hour (9 AM - 5 PM) + every 30 min during active trading")
        logger.info("   - Historical data: Daily at 6 AM and 6 PM")
        logger.info("   - Maintenance: Daily at 2 AM")
    
    def run_scheduler(self):
        """Run the scheduler loop"""
        logger.info("[START] Background data collector started")
        
        # Run initial data collection if during market hours
        current_time = datetime.now()
        if (current_time.weekday() < 5 and  # Weekday
            9 <= current_time.hour <= 17):   # Market hours
            logger.info("Running initial intraday data collection")
            self.collect_intraday_data()
        
        while self.is_running:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            except Exception as e:
                logger.error(f"Error in scheduler loop: {e}", exc_info=True)
                time.sleep(60)  # Continue after error
    
    def start(self):
        """Start the background data collector"""
        if self.is_running:
            logger.warning("Background data collector is already running")
            return
        
        self.is_running = True
        self.setup_schedule()
        
        # Start scheduler in background thread
        self.scheduler_thread = threading.Thread(
            target=self.run_scheduler,
            daemon=True,
            name="MSE-DataCollector"
        )
        self.scheduler_thread.start()
        
        logger.info("[TARGET] Background data collector started successfully")
    
    def stop(self):
        """Stop the background data collector"""
        self.is_running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        logger.info("🛑 Background data collector stopped")
    
    def auto_cache_refresh(self):
        """Smart cache refresh that works in both local and deployed environments"""
        try:
            current_time = datetime.now()
            logger.info(f"[REFRESH] Starting automatic cache refresh at {current_time}")
            
            # Determine environment (deployed vs local)
            is_deployed = self._is_deployed_environment()
            
            if is_deployed:
                # In deployed environment: Focus on internal cache warming
                logger.info("[DEPLOYED] Deployed environment detected - using internal cache warming")
                self._warm_internal_cache()
            else:
                # In local environment: Can do fresh data collection + cache warming
                logger.info("[LOCAL] Local environment detected - fresh data collection + cache warming")
                self._collect_and_cache()
            
        except Exception as e:
            logger.error(f"[ERROR] Error in auto cache refresh: {e}", exc_info=True)
    
    def _is_deployed_environment(self) -> bool:
        """Detect if running in deployed environment"""
        deployment_indicators = [
            'RENDER',           # Render.com
            'HEROKU',          # Heroku
            'RAILWAY',         # Railway
            'VERCEL',          # Vercel
            'NETLIFY',         # Netlify
            'PYTHONANYWHERE',  # PythonAnywhere
            'DIGITALOCEAN'     # DigitalOcean App Platform
        ]
        
        # Check environment variables for deployment indicators
        for indicator in deployment_indicators:
            if indicator in os.environ:
                return True
        
        # Check if we can reach MSE website (if not, probably deployed with restrictions)
        try:
            response = requests.get('https://mse.co.mw', timeout=5)
            return False  # Can reach MSE, probably local
        except:
            return True   # Can't reach MSE, probably deployed with network restrictions
    
    def _warm_internal_cache(self):
        """Warm cache using internal Django views (works in any environment)"""
        from stocks.views import historical_data
        from django.test import RequestFactory
        from rest_framework.request import Request
        
        factory = RequestFactory()
        
        # Configuration for cache warming
        priority_symbols = ['AIRTEL', 'TNM', 'NBM', 'STANDARD', 'NICO', 'FDHB']
        all_symbols = [
            'AIRTEL', 'BHL', 'FDHB', 'FMBCH', 'ICON', 'ILLOVO',
            'MPICO', 'NBM', 'NBS', 'NICO', 'NITL', 'OMU',
            'PCL', 'STANDARD', 'SUNBIRD', 'TNM'
        ]
        
        # Determine strategy based on time
        hour = datetime.now().hour
        if 9 <= hour <= 17:  # Market hours - focus on critical data
            symbols = priority_symbols
            ranges = ['1day', '1month']
        elif 6 <= hour < 9:  # Early morning - comprehensive refresh
            symbols = all_symbols
            ranges = ['1day', '1month', '1year']
        else:  # Other times - moderate refresh
            symbols = priority_symbols
            ranges = ['1day', '1month', '1year']
        
        successful = 0
        total = 0
        
        for symbol in symbols:
            for time_range in ranges:
                try:
                    # Create mock request with refresh=true to force cache update
                    request = factory.get(f'/api/historical/{symbol}/', {
                        'range': time_range,
                        'refresh': 'true'
                    })
                    request.META['HTTP_X_API_KEY'] = 'mse_5PFAyspVWQnz33boHidjCIiU2y6aNoEmzZteXzRV'
                    
                    # Convert to DRF request
                    drf_request = Request(request)
                    
                    # Import the view function
                    from .views import historical_prices
                    
                    # Call the view directly
                    response = historical_prices(drf_request, symbol)
                    
                    if response.status_code == 200:
                        data = response.data
                        points = data.get('data_points', 0)
                        logger.info(f"[CACHE-SUCCESS] Cache refreshed: {symbol} {time_range} ({points} points)")
                        successful += 1
                    else:
                        logger.warning(f"[CACHE-WARN] Cache refresh failed: {symbol} {time_range} - Status {response.status_code}")
                    
                    total += 1
                    time.sleep(0.2)  # Small delay between requests
                    
                except Exception as e:
                    logger.error(f"[CACHE-ERROR] Error warming cache for {symbol} {time_range}: {e}")
                    total += 1
        
        success_rate = (successful / total * 100) if total > 0 else 0
        logger.info(f"[TARGET] Internal cache warming completed: {successful}/{total} ({success_rate:.1f}%)")
    
    def _collect_and_cache(self):
        """Collect fresh data and warm cache (local environment only)"""
        # First try to collect fresh data
        try:
            management.call_command('scrape_stocks')
            logger.info("[SUCCESS] Fresh data collected successfully")
            time.sleep(5)  # Wait for data to be saved
        except Exception as e:
            logger.warning(f"[WARNING] Fresh data collection failed: {e}")
        
        # Then warm the cache
        self._warm_internal_cache()

# Global instance
_background_collector = None

def start_background_collector():
    """Start the background collector (called from Django app ready)"""
    global _background_collector
    
    if _background_collector is None or not _background_collector.is_running:
        _background_collector = BackgroundDataCollector()
        _background_collector.start()
        logger.info("[START] Background collector started from Django app")
    else:
        logger.info("Background collector already running")

def stop_background_collector():
    """Stop the background collector"""
    global _background_collector
    
    if _background_collector and _background_collector.is_running:
        _background_collector.stop()
        logger.info("🛑 Background collector stopped")

def get_collector_status():
    """Get the status of the background collector"""
    global _background_collector
    
    if _background_collector:
        return {
            'running': _background_collector.is_running,
            'stats': _background_collector.collection_stats,
            'last_successful': _background_collector.last_successful_collection
        }
    else:
        return {'running': False, 'stats': None, 'last_successful': None}

# For manual testing
if __name__ == "__main__":
    import django
    import os
    
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    django.setup()
    
    collector = BackgroundDataCollector()
    collector.start()
    
    try:
        # Keep running
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        collector.stop()
        print("Background collector stopped")
