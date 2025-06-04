import requests
import logging
import json
from datetime import datetime, timedelta
import time
import re
import pickle
import os
from pathlib import Path

logger = logging.getLogger(__name__)

class MSEHistoricalService:
    """Service to fetch historical stock data from MSE API"""
    
    BASE_URL = "https://mse.today/api/company/{}/historical"
    LOGIN_URL = "https://mse.today/"
    
    VALID_RANGES = [
        '1month', '3months', '6months', '1year', 
        'ytd', '2years', '3years', '5years'
    ]
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Referer': 'https://mse.today/companies/',
            'sec-ch-ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin'
        })
        self.authenticated = False
        
        # Try to load cookies on initialization
        self.load_cookies()
        
    def authenticate(self):
        """Authenticate with the MSE website to get necessary cookies"""
        try:
            logger.info("Authenticating with MSE website...")
            
            # First request to get cf_clearance and other cookies
            response = self.session.get(self.LOGIN_URL)
            
            if response.status_code != 200:
                logger.error(f"Failed to access MSE website: {response.status_code}")
                return False
                
            # Check if we have the necessary cookies
            cookies = self.session.cookies.get_dict()
            logger.info(f"Received cookies: {list(cookies.keys())}")
            
            # We need at least cf_clearance and _ga cookies
            if 'cf_clearance' not in cookies:
                # The site might have Cloudflare protection
                logger.warning("Cloudflare protection detected - need manual cookies")
                return False
                
            logger.info("Successfully authenticated with MSE website")
            self.authenticated = True
            return True
            
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}", exc_info=True)
            return False
            
    def set_manual_cookies(self, cookie_string):
        """Set cookies manually from a browser session"""
        try:
            # Parse cookie string from browser
            cookie_dict = {}
            for cookie_part in cookie_string.split(';'):
                if '=' in cookie_part:
                    name, value = cookie_part.strip().split('=', 1)
                    cookie_dict[name] = value
            
            # Add cookies to session
            for name, value in cookie_dict.items():
                self.session.cookies.set(name, value, domain='mse.today')
                
            logger.info(f"Manually set cookies: {list(cookie_dict.keys())}")
            self.authenticated = True
            return True
            
        except Exception as e:
            logger.error(f"Error setting manual cookies: {str(e)}")
            return False
    
    def load_cookies(self):
        """Load saved cookies from file"""
        cookie_file = os.path.join(Path.home(), '.mse_cookies')
        
        try:
            if os.path.exists(cookie_file):
                with open(cookie_file, 'rb') as f:
                    self.session.cookies.update(pickle.load(f))
                    
                logger.info(f"Loaded cookies from {cookie_file}")
                self.authenticated = True
                return True
            else:
                logger.warning(f"No cookie file found at {cookie_file}")
                return False
        except Exception as e:
            logger.error(f"Error loading cookies: {str(e)}")
            return False

    def get_historical_data(self, symbol, time_range='1month'):
        """
        Fetch historical data for a symbol and time range
        
        Args:
            symbol (str): Stock symbol (e.g., TNM, AIRTEL)
            time_range (str): Time range to fetch
                Options: 1month, 3months, 6months, 1year, ytd, 2years, 3years, 5years
                
        Returns:
            dict: Processed historical data with company info and price series
        """
        if time_range not in self.VALID_RANGES:
            logger.warning(f"Invalid time range: {time_range}. Using default '1month'")
            time_range = '1month'
            
        # Make sure we're authenticated
        if not self.authenticated:
            success = self.authenticate()
            if not success:
                logger.error("Authentication failed - please set cookies manually")
                return None
                
        url = self.BASE_URL.format(symbol)
        params = {'range': time_range}
        
        # Update referer for this specific request
        self.session.headers.update({
            'Referer': f'https://mse.today/companies/{symbol}'
        })
        
        try:
            logger.info(f"Fetching {time_range} historical data for {symbol}")
            response = self.session.get(url, params=params)
            
            if response.status_code != 200:
                logger.error(f"Failed to fetch data: {response.status_code} - {response.text}")
                return None
                
            data = response.json()
            if not data or not isinstance(data, list) or len(data) == 0:
                logger.warning(f"Empty or invalid response for {symbol}")
                return None
                
            # Process the response into a cleaner format
            return self._process_response(data[0], time_range)
            
        except Exception as e:
            logger.error(f"Error fetching historical data: {str(e)}", exc_info=True)
            return None
            
    def _process_response(self, data, time_range):
        """Process API response into a cleaner format"""
        if not data or 'stockPrices' not in data:
            return None
            
        company_info = {
            'symbol': data.get('symbol'),
            'name': data.get('name'),
            'isin': data.get('isin'),
            'current_price': data.get('currentPrice'),
            'listing_date': data.get('listingDate'),
            'listing_price': data.get('listingPrice'),
            'market_cap': data.get('marketCap'),
            'shares_in_issue': data.get('sharesInIssue')
        }
        
        stock_prices = []
        for price in data.get('stockPrices', []):
            stock_prices.append({
                'date': price.get('date'),
                'open': price.get('open'),
                'high': price.get('high'),
                'low': price.get('low'),
                'close': price.get('close'),
                'volume': price.get('volume'),
                'turnover': price.get('turnover')  # Make sure turnover is extracted from the API response
            })
            
        return {
            'company': company_info,
            'time_range': time_range,
            'stock_prices': stock_prices,
            'retrieved_at': datetime.now().isoformat(),
            'data_points': len(stock_prices)
        }
        
    def save_to_database(self, symbol, historical_data):
        """Save historical data to database"""
        from stocks.models import HistoricalPrice, Company
        
        if not historical_data or 'stock_prices' not in historical_data:
            logger.warning(f"No data to save for {symbol}")
            return 0
            
        count = 0
        try:
            # Get company reference
            try:
                company = Company.objects.get(symbol__iexact=symbol)
            except Company.DoesNotExist:
                logger.warning(f"Company {symbol} not found in database")
                company = None
                
            # Process each price point
            for price in historical_data['stock_prices']:
                try:
                    date = datetime.strptime(price['date'], '%Y-%m-%d').date()
                    
                    defaults = {
                        'open_price': price['open'],
                        'high': price['high'],
                        'low': price['low'],
                        'close_price': price['close'],
                        'price': price['close'],  # Use close as the main price
                        'volume': price['volume'],
                        'turnover': price['turnover'],  # Make sure turnover is included here
                        'company': company
                    }
                    
                    # Create or update historical price
                    obj, created = HistoricalPrice.objects.update_or_create(
                        symbol=symbol,
                        date=date,
                        defaults=defaults
                    )
                    
                    count += 1
                    
                except Exception as e:
                    logger.error(f"Error saving price data for {date}: {str(e)}")
                    continue
                    
            return count
            
        except Exception as e:
            logger.error(f"Error saving historical data: {str(e)}", exc_info=True)
            return 0