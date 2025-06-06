import requests
from bs4 import BeautifulSoup
import re
import json
import logging
from datetime import datetime
from stocks.models import Company, HistoricalPrice
from django.db import transaction
import pickle
import os
from pathlib import Path

logger = logging.getLogger(__name__)

class MSEHistoricalService:
    """Service to fetch historical stock data from MSE API"""
    
    BASE_URL = "https://www.mse.mn/en/company/"
    VALID_RANGES = [
        '1month', '3months', '6months', '1year', 
        'ytd', '2years', '3years', '5years'
    ]
    
    def __init__(self):
        self.session = requests.Session()
        self.authenticated = False
        
        # Try to load cookies on initialization
        self.load_cookies()
        
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

    def set_manual_cookies(self, cookie_string):
        """Set cookies manually from a browser session"""
        try:
            # Clear existing cookies
            self.session.cookies.clear()
            
            # Split the cookie string into individual cookies
            cookies = cookie_string.split(';')
            
            # Iterate through the cookies and set them in the session
            for cookie in cookies:
                cookie = cookie.strip()
                if cookie:
                    name, value = cookie.split('=', 1)
                    self.session.cookies.set(name.strip(), value.strip())
            
            # Test the cookies by making a request to a protected page
            response = self.session.get(self.BASE_URL + 'TNM')  # Replace 'TNM' with a valid symbol
            if response.status_code == 200:
                self.authenticated = True
                logger.info("Successfully set manual cookies.")
                return True
            else:
                logger.error(f"Failed to authenticate with provided cookies. Status code: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"Error setting manual cookies: {e}")
            return False
    
    def get_historical_data(self, symbol, time_range):
        """
        Fetches historical stock data from the MSE website.
        
        Args:
            symbol (str): The stock symbol.
            time_range (str): The time range for the data (e.g., '1month', '3months').
        
        Returns:
            dict: A dictionary containing company information and stock prices, or None if an error occurs.
        """
        url = f"{self.BASE_URL}{symbol}?stock_history={time_range}"
        
        try:
            response = self.session.get(url)
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract company information
            company_info = self._extract_company_info(soup, symbol)
            
            # Extract stock prices
            stock_prices = self._extract_stock_prices(soup)
            
            if not stock_prices:
                logger.warning(f"No stock prices found for {symbol} in {time_range} range.")
                return None
            
            # Prepare the result
            result = {
                'company': company_info,
                'time_range': time_range,
                'stock_prices': stock_prices,
                'retrieved_at': datetime.now().isoformat()
            }
            
            logger.info(f"Successfully fetched historical data for {symbol} in {time_range} range.")
            return result
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error for {symbol} in {time_range} range: {e}")
            return None
        except Exception as e:
            logger.error(f"Error fetching historical data for {symbol} in {time_range} range: {e}")
            return None
    
    def _extract_company_info(self, soup, symbol):
        """Extracts company information from the BeautifulSoup object."""
        try:
            company = Company.objects.get(symbol=symbol)
            return {
                'symbol': company.symbol,
                'name': company.name,
                'listing_date': company.listed_date.isoformat() if company.listed_date else None,
                'listing_price': float(company.listing_price) if company.listing_price else None,
                'shares_in_issue': company.shares_in_issue
            }
        except Company.DoesNotExist:
            logger.warning(f"Company with symbol {symbol} not found in database.")
            return {'symbol': symbol}
        except Exception as e:
            logger.error(f"Error extracting company info for {symbol}: {e}")
            return {'symbol': symbol}
    
    def _extract_stock_prices(self, soup):
        """Extracts stock prices from the BeautifulSoup object."""
        stock_prices = []
        try:
            table = soup.find('table', {'id': 'stock-history'})
            if not table:
                logger.warning("Stock history table not found.")
                return stock_prices
            
            rows = table.find_all('tr')
            header = [th.text.strip() for th in rows[0].find_all('th')]
            
            for row in rows[1:]:
                cols = row.find_all('td')
                cols = [ele.text.strip() for ele in cols]
                
                # Extract data and handle potential errors
                try:
                    date_str = cols[0]
                    date = datetime.strptime(date_str, '%Y-%m-%d').date()
                    open_price = float(cols[1].replace(',', '')) if cols[1] else None
                    high = float(cols[2].replace(',', '')) if cols[2] else None
                    low = float(cols[3].replace(',', '')) if cols[3] else None
                    close_price = float(cols[4].replace(',', '')) if cols[4] else None
                    volume = int(cols[5].replace(',', '')) if cols[5] else 0
                    turnover = float(cols[6].replace(',', '')) if cols[6] else None
                    
                    stock_prices.append({
                        'date': date,
                        'open': open_price,
                        'high': high,
                        'low': low,
                        'close': close_price,
                        'volume': volume,
                        'turnover': turnover
                    })
                except ValueError as ve:
                     logger.warning(f"ValueError processing row: {cols}. Error: {ve}")
                except Exception as e:
                    logger.error(f"Error processing row: {cols}. Error: {e}")
        except Exception as e:
            logger.error(f"Error extracting stock prices: {e}")
        
        return stock_prices
    
    @transaction.atomic
    def save_to_database(self, symbol, historical_data):
        """Saves historical data to the database."""
        if not historical_data or 'stock_prices' not in historical_data:
            logger.warning(f"No historical data to save for {symbol}.")
            return 0
        
        try:
            company = Company.objects.get(symbol=symbol)
        except Company.DoesNotExist:
            logger.warning(f"Company with symbol {symbol} not found in database.")
            return 0
        
        saved_count = 0
        for price_data in historical_data['stock_prices']:
            try:
                # Check if the HistoricalPrice already exists
                historical_price, created = HistoricalPrice.objects.get_or_create(
                    symbol=symbol,
                    date=price_data['date'],
                    defaults={
                        'company': company,
                        'open_price': price_data['open'],
                        'high': price_data['high'],
                        'low': price_data['low'],
                        'close_price': price_data['close'],
                        'volume': price_data['volume'],
                        'turnover': price_data['turnover'] if 'turnover' in price_data else None,
                        'last_updated': datetime.now()
                    }
                )
                if created:
                    saved_count += 1
                else:
                    # Update the existing HistoricalPrice
                    historical_price.open_price = price_data['open']
                    historical_price.high = price_data['high']
                    historical_price.low = price_data['low']
                    historical_price.close_price = price_data['close']
                    historical_price.volume = price_data['volume']
                    historical_price.turnover = price_data['turnover'] if 'turnover' in price_data else None,
                    historical_price.last_updated = datetime.now()
                    historical_price.save()
                    
            except Exception as e:
                logger.error(f"Error saving historical price for {symbol} on {price_data['date']}: {e}")
        
        logger.info(f"Saved {saved_count} historical prices for {symbol}.")
        return saved_count