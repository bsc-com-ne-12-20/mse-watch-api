import requests
import re
import pandas as pd
import os
from datetime import datetime
from bs4 import BeautifulSoup
import traceback

def extract_mse_data_html():
    """Extract stock data from the Malawi Stock Exchange website using HTML download."""
    url = "https://mse.co.mw/"
    html_file = "temp_mse.html"
    
    try:
        print(f"Downloading HTML from {url}...")
        # Download the HTML
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Raise an exception for bad responses
        
        # Save HTML to a temporary file
        with open(html_file, "w", encoding="utf-8") as f:
            f.write(response.text)
        print(f"HTML saved to {html_file}")
        
        # Parse HTML with BeautifulSoup
        print("Extracting data from HTML...")
        with open(html_file, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f.read(), 'html.parser')
        
        # Get market status and update time
        update_time = "Unknown"
        market_status = "Unknown"
        
        # Try to find the update time
        update_time_elem = soup.select_one("div.time span:-soup-contains('/')")
        if update_time_elem:
            update_time = update_time_elem.text.strip()
            print(f"Market data updated on: {update_time}")
        
        # Try to find market status
        try:
            market_status_elem = soup.select_one("span:-soup-contains('Market Status:') + span")
            if market_status_elem:
                market_status = market_status_elem.text.strip()
            else:
                market_status_elem = soup.select_one("div.time div small span")
                if market_status_elem:
                    market_status = market_status_elem.text.replace('Market Status: ', '').strip()
        except:
            pass
            
        print(f"Market Status: {market_status}")
        
        # Find ticker items containing stocks
        ticker_items = soup.select("div.ticker__item")
        print(f"Found {len(ticker_items)} ticker items")
        
        # Extract stock data
        data = []
        equity_count = 0
        max_equities = 16  # Limit to first 16 stocks
        
        for i, item in enumerate(ticker_items):
            # Stop if we've collected the maximum number of equities
            if equity_count >= max_equities:
                break
                
            try:
                # Get symbol (first span)
                symbol_span = item.select_one("span:first-child")
                if not symbol_span:
                    continue
                
                symbol = symbol_span.text.strip()
                if not symbol:
                    continue
                
                # Get price span and change span
                price_span = item.select_one("span.pricedata")
                change_span = item.select_one("span.changedata")
                
                if not price_span or not change_span:
                    print(f"Item {i+1} missing price or change span, skipping")
                    continue
                
                print(f"Processing stock: {symbol}")
                
                # Extract price (remove commas)
                price_text = price_span.text.strip().replace(',', '')
                try:
                    price = float(price_text) if price_text else None
                except ValueError:
                    print(f"Warning: Could not parse price for {symbol}: '{price_text}'")
                    price = None
                
                # Extract change value
                change_text = change_span.text.strip()
                change_match = re.search(r"\(([-+]?\d+(?:\.\d+)?)\)", change_text)
                try:
                    change = float(change_match.group(1)) if change_match else 0.0
                except (ValueError, AttributeError):
                    print(f"Warning: Could not parse change for {symbol}: '{change_text}'")
                    change = 0.0
                
                # Get direction
                if "changeup" in price_span.get("class", []):
                    direction = "up"
                elif "changedown" in price_span.get("class", []):
                    direction = "down"
                else:
                    direction = "no change"
                
                # Add to data
                data.append({
                    'Symbol': symbol,
                    'Price': price,
                    'Change': change,
                    'Direction': direction
                })
                
                print(f"Added {symbol} with price={price}, change={change}, direction={direction}")
                
                # Increment the equity counter
                equity_count += 1
                
            except Exception as e:
                print(f"Error processing item {i+1}: {e}")
        
        # Create DataFrame
        if data:
            df = pd.DataFrame(data)
            
            # Add metadata
            current_time = datetime.now()
            df['Date'] = current_time.strftime('%Y-%m-%d')
            df['Time'] = current_time.strftime('%H:%M:%S')
            df['Market_Status'] = market_status
            df['Market_Update_Time'] = update_time
            
            # Filter out any rows with NaN values in Symbol or Price
            df = df.dropna(subset=['Symbol', 'Price'])
            
            print(f"Successfully extracted data for {len(df)} stocks")
            return df
        else:
            print("No stock data found")
            return None
            
    except Exception as e:
        print(f"Error extracting data: {e}")
        traceback.print_exc()
        return None
        
    finally:
        # Delete the temporary HTML file
        if os.path.exists(html_file):
            os.remove(html_file)
            print(f"Deleted temporary file {html_file}")

def save_data(df):
    """
    Save the extracted data to CSV
    """
    if df is None:
        return
    
    # Create a directory for the data if it doesn't exist
    os.makedirs('data', exist_ok=True)
    
    # Generate filename with today's date
    filename = f"data/mse_data_html_{datetime.now().strftime('%Y%m%d')}.csv"
    
    # Save to CSV
    df.to_csv(filename, index=False)
    print(f"Data saved to {filename}")
    
    # Also save to a consolidated file
    consolidated_file = "data/mse_data_html_all.csv"
    
    if os.path.exists(consolidated_file):
        # Append without writing headers
        df.to_csv(consolidated_file, mode='a', header=False, index=False)
    else:
        # Create new file with headers
        df.to_csv(consolidated_file, index=False)
    
    print(f"Data appended to {consolidated_file}")

def save_to_database(df):
    """
    Save the extracted data to the database
    """
    import os
    import django
    import sys

    # Only set up Django if it's not already set up
    # This is needed when running the scraper directly
    if 'django.apps' not in sys.modules:
        # Set up Django environment
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mse_api.settings")
        django.setup()

    # Import the model after Django setup
    from stocks.models import StockPrice
    from datetime import datetime

    if df is None:
        print("No data to save to database")
        return 0

    count = 0
    for _, row in df.iterrows():
        try:
            # Parse date and time from strings
            date = datetime.strptime(row['Date'], '%Y-%m-%d').date()
            time_obj = datetime.strptime(row['Time'], '%H:%M:%S').time()
            
            # Create or update stock price entry
            StockPrice.objects.update_or_create(
                symbol=row['Symbol'],
                date=date,
                time=time_obj,
                defaults={
                    'price': row['Price'],
                    'change': row['Change'],
                    'direction': row['Direction'],
                    'market_status': row['Market_Status'],
                    'market_update_time': row['Market_Update_Time']
                }
            )
            count += 1
        except Exception as e:
            print(f"Error saving {row['Symbol']} to database: {e}")
    
    print(f"Saved {count} stock prices to database")
    return count

if __name__ == "__main__":
    df = extract_mse_data_html()
    if df is not None:
        print(f"Successfully extracted data for {len(df)} stocks:")
        print(df)
        save_data(df)  # Save to CSV
        save_to_database(df)  # Save to database
    else:
        print("Failed to extract data.")