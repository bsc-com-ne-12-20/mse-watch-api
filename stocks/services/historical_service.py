import requests
from bs4 import BeautifulSoup
import re
import json
import logging
from datetime import datetime, date, timedelta
from stocks.models import Company, HistoricalPrice
from django.db import transaction
from django.core.cache import cache
import time

logger = logging.getLogger(__name__)

class MSEHistoricalService:
    """Service to fetch historical stock data from MSE website"""
    
    BASE_URL = "https://mse.co.mw/company/"
      # Time period mapping: API parameter -> months
    TIME_PERIOD_MAP = {
        '1day': 0,  # Special case for intraday data
        '1month': 1,
        '3months': 3, 
        '6months': 6,
        '1year': 12,
        '2years': 24,
        '5years': 60
    }
    
    def __init__(self):
        self.session = requests.Session()
        # Set headers to mimic a real browser
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html, */*; q=0.01',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',        })
        
    def get_company_id_from_symbol(self, symbol):
        """
        Map stock symbol to MSE company ID.
        These are the actual company IDs from the MSE website.
        """
        # Complete mappings for all MSE-listed companies
        symbol_to_id = {
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
        
        return symbol_to_id.get(symbol.upper())
    
    def get_historical_data(self, symbol, time_range):
        """
        Fetch historical stock data from MSE website
        
        Args:
            symbol (str): Stock symbol
            time_range (str): Time range (1month, 3months, 6months, 1year, 2years, 5years)
            
        Returns:
            dict: Historical data or None if error
        """        # Handle intraday (1day) data specially
        if time_range == '1day':
            logger.info(f"Fetching intraday data for {symbol}")
            return self.get_intraday_data(symbol)
            
        # Check cache first for historical data
        cache_key = f"historical_{symbol}_{time_range}_{date.today().isoformat()}"
        cached_data = cache.get(cache_key)
        if cached_data:
            logger.info(f"Returning cached data for {symbol} {time_range}")
            return cached_data
            
        # Get company ID
        company_id = self.get_company_id_from_symbol(symbol)
        if not company_id:
            logger.error(f"No company ID mapping found for symbol: {symbol}")
            return None
              # Get time period number
        period_num = self.TIME_PERIOD_MAP.get(time_range)
        if period_num is None:
            logger.error(f"Invalid time range: {time_range}")
            return None
            
        # Build URL and make request
        url = f"{self.BASE_URL}{company_id}/{period_num}"
        
        try:
            # Set additional headers for this specific request
            headers = {
                'Referer': f"{self.BASE_URL}{company_id}",
                'Origin': 'https://mse.co.mw',
                'X-Requested-With': 'XMLHttpRequest',
            }
            
            logger.info(f"Fetching data from: {url}")
            response = self.session.post(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            # Parse the response to extract chart data
            chart_data = self._extract_chart_data(response.text, symbol)
            
            if not chart_data:
                logger.warning(f"No chart data found for {symbol} in {time_range}")
                return None
            
            # Check if we have sufficient data for the requested time range
            expected_points = self._get_expected_data_points(time_range)
            actual_points = len(chart_data)
            data_limitation = None
            
            if actual_points < expected_points * 0.7:  # Less than 70% of expected data
                data_limitation = f"Limited data available: {actual_points} points (expected ~{expected_points})"
                logger.warning(f"Limited data for {symbol} {time_range}: {actual_points}/{expected_points} points")
                
            # Prepare result
            result = {
                'company': {
                    'symbol': symbol,
                    'name': self._get_company_name(symbol),
                },
                'time_range': time_range,
                'stock_prices': chart_data,
                'retrieved_at': datetime.now().isoformat(),
                'data_points': len(chart_data),
                'source': 'mse.co.mw'
            }
            
            # Add data limitation warning if applicable
            if data_limitation:
                result['data_limitation'] = data_limitation
                result['note'] = "MSE website may not have complete historical data for this time range"
            
            # Cache the result for 6 hours for recent data, 24 hours for older data
            cache_timeout = 21600 if time_range in ['1month', '3months'] else 86400
            cache.set(cache_key, result, cache_timeout)
            
            logger.info(f"Successfully fetched {len(chart_data)} data points for {symbol} {time_range}")
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed for {symbol} {time_range}: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error fetching data for {symbol} {time_range}: {str(e)}")
            return None
    
    def _extract_chart_data(self, html_content, symbol):
        """
        Extract chart data from the HTML response
        """
        try:
            # Look for the JSON data in the JavaScript
            # The data is in the format: var json = [{"label":"Price","data":[...]}]
            pattern = r'var\s+json\s*=\s*(\[.*?\]);'
            match = re.search(pattern, html_content, re.DOTALL)
            
            if not match:
                # Try alternative pattern for the datasets
                pattern = r'"datasets":\s*(\[.*?\])'
                match = re.search(pattern, html_content, re.DOTALL)
                
            if not match:
                logger.warning(f"Could not find chart data pattern in response for {symbol}")
                return []
                
            # Parse the JSON data
            json_str = match.group(1)
            chart_datasets = json.loads(json_str)
            
            # Extract price data
            price_data = []
            
            if isinstance(chart_datasets, list) and len(chart_datasets) > 0:
                dataset = chart_datasets[0]
                if 'data' in dataset:
                    data_points = dataset['data']
                    
                    for point in data_points:
                        if isinstance(point, dict) and 'x' in point and 'y' in point:
                            try:
                                # Parse date (format: "21-May-2025")
                                date_str = point['x']
                                price_date = datetime.strptime(date_str, "%d-%b-%Y").date()
                                price_value = float(point['y'])
                                
                                price_data.append({
                                    'date': price_date.isoformat(),
                                    'price': price_value,
                                    'close': price_value,  # Using price as close for now
                                    'open': None,
                                    'high': None,
                                    'low': None,
                                    'volume': None,
                                    'turnover': None
                                })
                            except (ValueError, KeyError) as e:
                                logger.warning(f"Error parsing data point {point}: {e}")
                                continue
                                
            # Sort by date (oldest first)
            price_data.sort(key=lambda x: x['date'])
            
            return price_data
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            return []
        except Exception as e:
            logger.error(f"Error extracting chart data: {e}")
            return []
    
    def _get_company_name(self, symbol):
        """Get company name from database or return symbol"""
        try:
            company = Company.objects.get(symbol=symbol)
            return company.name
        except Company.DoesNotExist:
            return symbol
    
    @transaction.atomic
    def save_to_database(self, symbol, historical_data):
        """Save historical data to database"""
        if not historical_data or 'stock_prices' not in historical_data:
            logger.warning(f"No historical data to save for {symbol}")
            return 0
            
        # Get or create company
        try:
            company = Company.objects.get(symbol=symbol)
        except Company.DoesNotExist:
            logger.warning(f"Company {symbol} not found in database")
            company = None
            
        saved_count = 0
        for price_data in historical_data['stock_prices']:
            try:
                price_date = datetime.fromisoformat(price_data['date']).date()
                
                # Create or update historical price
                historical_price, created = HistoricalPrice.objects.update_or_create(
                    symbol=symbol,
                    date=price_date,
                    defaults={
                        'company': company,
                        'price': price_data['price'],
                        'close_price': price_data['close'],
                        'open_price': price_data.get('open'),
                        'high': price_data.get('high'),
                        'low': price_data.get('low'),
                        'volume': price_data.get('volume'),
                        'turnover': price_data.get('turnover'),
                        'last_updated': datetime.now()
                    }
                )
                
                if created:
                    saved_count += 1
                    
            except Exception as e:
                logger.error(f"Error saving price data for {symbol} on {price_data.get('date')}: {e}")
                
        logger.info(f"Saved {saved_count} new historical prices for {symbol}")
        return saved_count
    
    def _get_expected_data_points(self, time_range):
        """Get expected number of data points for a time range (assuming ~20 trading days per month)"""
        expected_map = {
            '1month': 22,
            '3months': 60,
            '6months': 120,
            '1year': 240,
            '2years': 480,
            '5years': 1200        }
        return expected_map.get(time_range, 22)
    
    def get_intraday_data(self, symbol, target_date=None):
        """
        Get intraday data for a specific trading day from StockPrice model
        
        Args:
            symbol (str): Stock symbol
            target_date (date): Specific date to get data for (defaults to today)
            
        Returns:
            dict: Intraday data for the specified day
        """
        from datetime import date
        
        if target_date is None:
            target_date = date.today()
        
        # Get all prices for this symbol from the target date, ordered by time
        from stocks.models import StockPrice
        intraday_prices = StockPrice.objects.filter(
            symbol=symbol.upper(),
            date=target_date
        ).order_by('time').values(
            'price', 'time', 'change', 'direction', 'market_status'
        )
        
        # If no data for today, try yesterday (most recent trading day)
        if not intraday_prices and target_date == date.today():
            recent_date = StockPrice.objects.filter(
                symbol=symbol.upper()
            ).values_list('date', flat=True).order_by('-date').first()
            
            if recent_date:
                target_date = recent_date
                intraday_prices = StockPrice.objects.filter(
                    symbol=symbol.upper(),
                    date=target_date
                ).order_by('time').values(
                    'price', 'time', 'change', 'direction', 'market_status'
                )
        
        if not intraday_prices:
            return None
            return None
            
        # Convert to list and format times
        price_data = []
        for price in intraday_prices:
            price_data.append({
                'time': price['time'].strftime('%H:%M:%S'),
                'price': float(price['price']),
                'change': float(price['change']),
                'direction': price['direction'],
                'market_status': price['market_status']
            })
          # Calculate OHLC from intraday data
        prices = [p['price'] for p in price_data]
        if prices:
            open_price = prices[0]
            high_price = max(prices)
            low_price = min(prices)
            close_price = prices[-1]
        else:
            open_price = high_price = low_price = close_price = 0
            
        return {
            'symbol': symbol.upper(),
            'date': target_date.isoformat(),
            'open': open_price,
            'high': high_price,
            'low': low_price,
            'close': close_price,
            'intraday_prices': price_data,
            'data_points': len(price_data),
            'market_sessions': self._identify_market_sessions(price_data)
        }
    
    def _identify_market_sessions(self, price_data):
        """Identify which market session each price belongs to"""
        sessions = []
        for price in price_data:
            time_str = price['time']
            hour, minute, _ = map(int, time_str.split(':'))
            time_minutes = hour * 60 + minute
            
            if 540 <= time_minutes < 570:  # 09:00-09:30
                session = 'Pre-Open'
            elif 570 <= time_minutes < 870:  # 09:30-14:30
                session = 'Open'
            elif 870 <= time_minutes < 900:  # 14:30-15:00
                session = 'Close'
            elif 900 <= time_minutes < 1020:  # 15:00-17:00
                session = 'Post-Close'
            else:
                session = 'After-Hours'
                
            sessions.append(session)
            
        return list(set(sessions))  # Return unique sessions