#!/usr/bin/env python3
"""
Daily Cache Refresh - Simple Version

Refreshes the most important cached data daily.
Optimized for automated daily runs via Task Scheduler or cron.
"""

import requests
import time
import logging
from datetime import datetime

# Configuration
BASE_URL = "http://127.0.0.1:8000/api/historical"
API_KEY = "mse_5PFAyspVWQnz33boHidjCIiU2y6aNoEmzZteXzRV"

# Priority symbols (most actively traded)
PRIORITY_SYMBOLS = ['AIRTEL', 'TNM', 'NBM', 'STANDARD', 'NICO', 'FDHB']

# All symbols
ALL_SYMBOLS = [
    'AIRTEL', 'BHL', 'FDHB', 'FMBCH', 'ICON', 'ILLOVO',
    'MPICO', 'NBM', 'NBS', 'NICO', 'NITL', 'OMU',
    'PCL', 'STANDARD', 'SUNBIRD', 'TNM'
]

# Daily refresh strategy: Most important ranges
DAILY_RANGES = ['1day', '1month', '1year']

HEADERS = {
    'X-API-Key': API_KEY,
    'Content-Type': 'application/json'
}

# Setup logging with UTF-8 encoding for Windows compatibility
log_file = f"daily_refresh_{datetime.now().strftime('%Y%m%d')}.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def refresh_endpoint(symbol, time_range):
    """Refresh a single endpoint"""
    url = f"{BASE_URL}/{symbol}/"
    params = {'range': time_range, 'refresh': 'true'}
    
    try:
        logger.info(f"Refreshing {symbol} - {time_range}")
        response = requests.get(url, params=params, headers=HEADERS, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            points = data.get('data_points', 0)
            logger.info(f"[SUCCESS] {symbol} {time_range}: {points} data points refreshed")
            return True
        else:
            logger.error(f"[ERROR] {symbol} {time_range}: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"[ERROR] {symbol} {time_range}: {str(e)}")
        return False

def daily_refresh():
    """Perform daily cache refresh"""
    start_time = datetime.now()
    logger.info("[START] Starting daily cache refresh")
    
    total_requests = 0
    successful = 0
    
    # Phase 1: Priority symbols with critical ranges
    logger.info("[PHASE-1] Priority symbols (most important data)")
    for symbol in PRIORITY_SYMBOLS:
        for time_range in DAILY_RANGES:
            if refresh_endpoint(symbol, time_range):
                successful += 1
            total_requests += 1
            time.sleep(0.5)  # Small delay to avoid overwhelming server
    
    # Phase 2: Remaining symbols with reduced ranges
    logger.info("[PHASE-2] Remaining symbols (essential data)")
    remaining_symbols = [s for s in ALL_SYMBOLS if s not in PRIORITY_SYMBOLS]
    essential_ranges = ['1day', '1month']  # Only most essential for remaining symbols
    
    for symbol in remaining_symbols:
        for time_range in essential_ranges:
            if refresh_endpoint(symbol, time_range):
                successful += 1
            total_requests += 1
            time.sleep(0.3)  # Slightly faster for remaining symbols
    
    # Summary
    duration = datetime.now() - start_time
    success_rate = (successful / total_requests * 100) if total_requests > 0 else 0
    
    logger.info("=" * 50)
    logger.info("[COMPLETE] DAILY REFRESH COMPLETE")
    logger.info(f"Duration: {duration}")
    logger.info(f"Total requests: {total_requests}")
    logger.info(f"Successful: {successful}")
    logger.info(f"Failed: {total_requests - successful}")
    logger.info(f"Success rate: {success_rate:.1f}%")
    logger.info("=" * 50)
    
    return successful, total_requests

if __name__ == "__main__":
    try:
        successful, total = daily_refresh()
        
        # Exit with appropriate code for monitoring
        if successful == total:
            exit(0)  # Perfect success
        elif successful > total * 0.8:
            exit(0)  # Acceptable success rate (80%+)
        else:
            exit(1)  # Too many failures
            
    except Exception as e:
        logger.error(f"[FATAL] Fatal error: {e}")
        exit(1)
