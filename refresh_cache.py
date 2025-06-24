#!/usr/bin/env python3
"""
MSE Cache Refresh Script

This script refreshes cached historical data for all supported symbols and time ranges.
Designed to run daily via cron job or task schedu        print("=" * 60)
        print("CACHE REFRESH SUMMARY")
        print("=" * 60)
        print(f"Duration: {duration}")
        print(f"Total Requests: {self.stats['total_requests']}")
        print(f"Successful: {self.stats['successful']}")
        print(f"Failed: {self.stats['failed']}")
        print(f"Success Rate: {(self.stats['successful']/self.stats['total_requests']*100):.1f}%")eep cache fresh.

Usage:
    python refresh_cache.py --all                    # Refresh all symbols and ranges
    python refresh_cache.py --symbols AIRTEL,NBM     # Specific symbols only
    python refresh_cache.py --ranges 1day,1month     # Specific ranges only
    python refresh_cache.py --dry-run                # Show what would be done
"""

import requests
import time
import argparse
import logging
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import json

# Configuration
BASE_URL = "http://127.0.0.1:8000/api/historical"
API_KEY = "mse_5PFAyspVWQnz33boHidjCIiU2y6aNoEmzZteXzRV"

# All supported symbols on MSE
ALL_SYMBOLS = [
    'AIRTEL', 'BHL', 'FDHB', 'FMBCH', 'ICON', 'ILLOVO',
    'MPICO', 'NBM', 'NBS', 'NICO', 'NITL', 'OMU',
    'PCL', 'STANDARD', 'SUNBIRD', 'TNM'
]

# All supported time ranges
ALL_RANGES = ['1day', '1month', '3months', '6months', '1year', '2years', '5years']

# Priority order for refresh (most important first)
PRIORITY_RANGES = ['1day', '1month', '1year', '3months', '6months', '2years', '5years']

# Request configuration
HEADERS = {
    'X-API-Key': API_KEY,
    'Content-Type': 'application/json',
    'User-Agent': 'MSE-Cache-Refresh/1.0'
}

# Logging setup with Windows console compatibility
import sys
import os

# Configure logging with UTF-8 encoding
if os.name == 'nt':  # Windows
    # For Windows console
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('cache_refresh.log', encoding='utf-8')
        ]
    )
    # Set console to UTF-8 if possible
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass
else:
    # For Unix/Linux
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('cache_refresh.log', encoding='utf-8')
        ]
    )
logger = logging.getLogger(__name__)

class CacheRefresher:
    def __init__(self, base_url=BASE_URL, api_key=API_KEY, max_workers=3):
        self.base_url = base_url
        self.headers = {'X-API-Key': api_key, 'Content-Type': 'application/json'}
        self.max_workers = max_workers
        self.stats = {
            'total_requests': 0,
            'successful': 0,
            'failed': 0,
            'start_time': None,
            'end_time': None
        }

    def refresh_single(self, symbol, time_range, delay=0.5):
        """Refresh cache for a single symbol and time range"""
        if delay > 0:
            time.sleep(delay)
            
        url = f"{self.base_url}/{symbol}/"
        params = {'range': time_range, 'refresh': 'true'}
        
        try:
            logger.info(f"[REFRESH] Refreshing {symbol} - {time_range}")
            response = requests.get(url, params=params, headers=self.headers, timeout=60)
            
            self.stats['total_requests'] += 1
            
            if response.status_code == 200:
                data = response.json()
                data_points = data.get('data_points', 0)
                source = data.get('source', 'unknown')
                logger.info(f"[SUCCESS] {symbol} {time_range}: {data_points} points (source: {source})")
                self.stats['successful'] += 1
                return True, f"{symbol}-{time_range}: Success ({data_points} points)"
            else:
                error_msg = f"{symbol}-{time_range}: HTTP {response.status_code}"
                logger.error(f"[ERROR] {error_msg}")
                self.stats['failed'] += 1
                return False, error_msg
                
        except requests.exceptions.Timeout:
            error_msg = f"{symbol}-{time_range}: Request timeout"
            logger.error(f"[TIMEOUT] {error_msg}")
            self.stats['failed'] += 1
            return False, error_msg
            
        except Exception as e:
            error_msg = f"{symbol}-{time_range}: {str(e)}"
            logger.error(f"[ERROR] {error_msg}")
            self.stats['failed'] += 1
            return False, error_msg

    def refresh_batch(self, symbols, ranges, dry_run=False):
        """Refresh cache for multiple symbols and ranges"""
        self.stats['start_time'] = datetime.now()
        
        # Create all combinations
        tasks = []
        for symbol in symbols:
            for time_range in ranges:
                tasks.append((symbol, time_range))
        
        total_tasks = len(tasks)
        logger.info(f"[START] Starting cache refresh for {len(symbols)} symbols x {len(ranges)} ranges = {total_tasks} requests")
        
        if dry_run:
            logger.info("[DRY-RUN] DRY RUN MODE - No actual requests will be made")
            for symbol, time_range in tasks:
                print(f"  Would refresh: {symbol} - {time_range}")
            return
        
        # Execute requests with controlled concurrency
        results = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks with delays to avoid overwhelming the server
            future_to_task = {}
            for i, (symbol, time_range) in enumerate(tasks):
                delay = i * 0.1  # 100ms delay between request starts
                future = executor.submit(self.refresh_single, symbol, time_range, delay)
                future_to_task[future] = (symbol, time_range)
            
            # Collect results
            for future in as_completed(future_to_task):
                symbol, time_range = future_to_task[future]
                try:
                    success, message = future.result()
                    results.append((symbol, time_range, success, message))
                except Exception as e:
                    error_msg = f"Future execution error: {e}"
                    logger.error(f"[FUTURE-ERROR] {symbol}-{time_range}: {error_msg}")
                    results.append((symbol, time_range, False, error_msg))
        
        self.stats['end_time'] = datetime.now()
        self._print_summary(results)
        return results

    def refresh_priority(self, symbols=None, dry_run=False):
        """Refresh cache in priority order (most important ranges first)"""
        if symbols is None:
            symbols = ALL_SYMBOLS
            
        logger.info("[PRIORITY] Running priority refresh (most important data first)")
        
        # Refresh 1day for all symbols first (most time-sensitive)
        logger.info("[PRIORITY-1] Priority 1: Refreshing 1day data for all symbols")
        self.refresh_batch(symbols, ['1day'], dry_run)
        
        # Then refresh other ranges
        for time_range in PRIORITY_RANGES[1:]:  # Skip 1day as we already did it
            logger.info(f"[PRIORITY-RANGE] Priority refresh: {time_range} for all symbols")
            self.refresh_batch(symbols, [time_range], dry_run)
            time.sleep(2)  # Short pause between ranges

    def _print_summary(self, results):
        """Print execution summary"""
        duration = self.stats['end_time'] - self.stats['start_time']
        
        print("\n" + "="*60)
        print("CACHE REFRESH SUMMARY")
        print("="*60)
        print(f"Duration: {duration}")
        print(f"Total Requests: {self.stats['total_requests']}")
        print(f"Successful: {self.stats['successful']}")
        print(f"Failed: {self.stats['failed']}")
        print(f"Success Rate: {(self.stats['successful']/self.stats['total_requests']*100):.1f}%")
        
        # Show failed requests if any
        failed_results = [r for r in results if not r[2]]
        if failed_results:
            print(f"\nFailed Requests ({len(failed_results)}):")
            for symbol, time_range, _, message in failed_results:
                print(f"  - {symbol}-{time_range}: {message}")
        
        print("=" * 60)

def main():
    parser = argparse.ArgumentParser(description='Refresh MSE historical data cache')
    parser.add_argument('--symbols', help='Comma-separated list of symbols (default: all)')
    parser.add_argument('--ranges', help='Comma-separated list of ranges (default: all)')
    parser.add_argument('--priority', action='store_true', help='Use priority refresh order')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done without making requests')
    parser.add_argument('--max-workers', type=int, default=3, help='Maximum concurrent requests (default: 3)')
    parser.add_argument('--all', action='store_true', help='Refresh all symbols and ranges')
    
    args = parser.parse_args()
    
    # Determine symbols and ranges
    if args.symbols:
        symbols = [s.strip().upper() for s in args.symbols.split(',')]
        # Validate symbols
        invalid_symbols = [s for s in symbols if s not in ALL_SYMBOLS]
        if invalid_symbols:
            logger.error(f"Invalid symbols: {invalid_symbols}")
            logger.info(f"Valid symbols: {', '.join(ALL_SYMBOLS)}")
            return 1
    else:
        symbols = ALL_SYMBOLS
    
    if args.ranges:
        ranges = [r.strip() for r in args.ranges.split(',')]
        # Validate ranges
        invalid_ranges = [r for r in ranges if r not in ALL_RANGES]
        if invalid_ranges:
            logger.error(f"Invalid ranges: {invalid_ranges}")
            logger.info(f"Valid ranges: {', '.join(ALL_RANGES)}")
            return 1
    else:
        ranges = ALL_RANGES if args.all else PRIORITY_RANGES
    
    # Create refresher
    refresher = CacheRefresher(max_workers=args.max_workers)
    
    # Run refresh
    try:
        if args.priority:
            refresher.refresh_priority(symbols, args.dry_run)
        else:
            refresher.refresh_batch(symbols, ranges, args.dry_run)
        return 0
    except KeyboardInterrupt:
        logger.info("[INTERRUPTED] Refresh interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"[FATAL-ERROR] Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
