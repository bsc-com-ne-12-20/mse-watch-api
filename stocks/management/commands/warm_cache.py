#!/usr/bin/env python3
"""
Django management command for warming the historical data cache.

Usage:
    python manage.py warm_cache --strategy priority
    python manage.py warm_cache --strategy intraday_only
    python manage.py warm_cache --strategy standard
    python manage.py warm_cache --strategy full
    python manage.py warm_cache --symbols AIRTEL,TNM --ranges 1day,1month
"""

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
import requests
import time
from datetime import datetime

class Command(BaseCommand):
    help = 'Warm the historical data cache by pre-loading API responses'

    def add_arguments(self, parser):
        parser.add_argument(
            '--strategy',
            type=str,
            choices=['priority', 'standard', 'full', 'intraday_only'],
            default='priority',
            help='Cache warming strategy'
        )
        parser.add_argument(
            '--symbols',
            type=str,
            help='Comma-separated list of symbols (overrides strategy)'
        )
        parser.add_argument(
            '--ranges',
            type=str,
            help='Comma-separated list of ranges (overrides strategy)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without making requests'
        )
        parser.add_argument(
            '--api-key',
            type=str,
            default='mse_5PFAyspVWQnz33boHidjCIiU2y6aNoEmzZteXzRV',
            help='API key to use for requests'
        )

    def handle(self, *args, **options):
        # Configuration
        base_url = 'http://127.0.0.1:8000/api/historical'
        api_key = options['api_key']
        
        all_symbols = [
            'AIRTEL', 'BHL', 'FDHB', 'FMBCH', 'ICON', 'ILLOVO',
            'MPICO', 'NBM', 'NBS', 'NICO', 'NITL', 'OMU',
            'PCL', 'STANDARD', 'SUNBIRD', 'TNM'
        ]
        
        priority_symbols = ['AIRTEL', 'TNM', 'NBM', 'STANDARD', 'NICO', 'FDHB']
        
        range_configs = {
            'priority': ['1day', '1month', '1year'],
            'standard': ['1day', '1month', '3months', '6months', '1year'],
            'full': ['1day', '1month', '3months', '6months', '1year', '2years', '5years'],
            'intraday_only': ['1day']
        }
        
        # Determine symbols and ranges
        if options['symbols']:
            symbols = [s.strip().upper() for s in options['symbols'].split(',')]
        else:
            strategy = options['strategy']
            if strategy == 'priority':
                symbols = priority_symbols
            else:
                symbols = all_symbols
        
        if options['ranges']:
            ranges = [r.strip() for r in options['ranges'].split(',')]
        else:
            ranges = range_configs[options['strategy']]
        
        # Validate symbols
        invalid_symbols = [s for s in symbols if s not in all_symbols]
        if invalid_symbols:
            raise CommandError(f"Invalid symbols: {invalid_symbols}")
        
        # Validate ranges
        valid_ranges = ['1day', '1month', '3months', '6months', '1year', '2years', '5years']
        invalid_ranges = [r for r in ranges if r not in valid_ranges]
        if invalid_ranges:
            raise CommandError(f"Invalid ranges: {invalid_ranges}")
        
        # Calculate total requests
        total_requests = len(symbols) * len(ranges)
        
        self.stdout.write(
            self.style.SUCCESS(f"Cache Warming Plan:")
        )
        self.stdout.write(f"  Strategy: {options['strategy']}")
        self.stdout.write(f"  Symbols: {', '.join(symbols)} ({len(symbols)} total)")
        self.stdout.write(f"  Ranges: {', '.join(ranges)} ({len(ranges)} total)")
        self.stdout.write(f"  Total requests: {total_requests}")
        
        if options['dry_run']:
            self.stdout.write(self.style.WARNING("DRY RUN MODE - No actual requests will be made"))
            for symbol in symbols:
                for time_range in ranges:
                    self.stdout.write(f"  Would warm: {symbol} - {time_range}")
            return
        
        # Execute cache warming
        start_time = datetime.now()
        successful = 0
        failed = 0
        
        headers = {
            'X-API-Key': api_key,
            'Content-Type': 'application/json'
        }
        
        self.stdout.write(self.style.SUCCESS(f"\nStarting cache warming..."))
        
        for i, symbol in enumerate(symbols):
            self.stdout.write(f"\nWarming cache for {symbol} ({i+1}/{len(symbols)}):")
            
            for time_range in ranges:
                try:
                    url = f"{base_url}/{symbol}/"
                    params = {'range': time_range, 'refresh': 'true'}
                    
                    self.stdout.write(f"  {symbol} {time_range}... ", ending='')
                    
                    response = requests.get(url, params=params, headers=headers, timeout=30)
                    
                    if response.status_code == 200:
                        data = response.json()
                        points = data.get('data_points', 0)
                        source = data.get('source', 'unknown')
                        self.stdout.write(
                            self.style.SUCCESS(f"✓ {points} points (source: {source})")
                        )
                        successful += 1
                    else:
                        self.stdout.write(
                            self.style.ERROR(f"✗ HTTP {response.status_code}")
                        )
                        failed += 1
                        
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f"✗ Error: {str(e)}")
                    )
                    failed += 1
                
                # Small delay to be nice to the server
                time.sleep(0.2)
        
        # Summary
        duration = datetime.now() - start_time
        success_rate = (successful / total_requests * 100) if total_requests > 0 else 0
        
        self.stdout.write(f"\n" + "="*60)
        self.stdout.write(self.style.SUCCESS("CACHE WARMING COMPLETE"))
        self.stdout.write("="*60)
        self.stdout.write(f"Duration: {duration}")
        self.stdout.write(f"Total requests: {total_requests}")
        self.stdout.write(
            self.style.SUCCESS(f"Successful: {successful}") if successful > 0 else "Successful: 0"
        )
        self.stdout.write(
            self.style.ERROR(f"Failed: {failed}") if failed > 0 else "Failed: 0"
        )
        self.stdout.write(f"Success rate: {success_rate:.1f}%")
        self.stdout.write("="*60)
        
        if success_rate >= 90:
            self.stdout.write(self.style.SUCCESS("Cache warming completed successfully!"))
        elif success_rate >= 70:
            self.stdout.write(self.style.WARNING("Cache warming completed with some issues."))
        else:
            self.stdout.write(self.style.ERROR("Cache warming had significant failures."))
