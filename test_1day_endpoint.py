#!/usr/bin/env python3
"""
Test script for the new 1day historical endpoint
"""
import requests
import json
from datetime import datetime

# Test configuration
BASE_URL = "http://localhost:8000/api/stocks"
TEST_SYMBOL = "AIRTEL"  # Use a known symbol
API_KEY = "mse_5PFAyspVWQnz33boHidjCIiU2y6aNoEmzZteXzRV"  # Test API key

HEADERS = {
    'X-API-Key': API_KEY,
    'Content-Type': 'application/json'
}

def test_1day_endpoint():
    """Test the 1day range parameter"""
    print(f"🧪 Testing 1day endpoint for {TEST_SYMBOL}")
    print("=" * 50)
    
    # Test the 1day endpoint
    url = f"{BASE_URL}/historical/{TEST_SYMBOL}/"
    params = {"range": "1day"}
    
    try:        print(f"📡 Making request to: {url}")
        print(f"📋 Parameters: {params}")
        
        response = requests.get(url, params=params, headers=HEADERS, timeout=30)
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            print("✅ Success! 1day endpoint is working")
            print(f"📈 Symbol: {data.get('symbol', 'N/A')}")
            print(f"📅 Date: {data.get('date', 'N/A')}")
            print(f"💰 Open: {data.get('open', 'N/A')}")
            print(f"📈 High: {data.get('high', 'N/A')}")
            print(f"📉 Low: {data.get('low', 'N/A')}")
            print(f"💰 Close: {data.get('close', 'N/A')}")
            print(f"📊 Data Points: {data.get('data_points', 'N/A')}")
            
            # Show market sessions if available
            if 'market_sessions' in data:
                print(f"🕐 Market Sessions: {', '.join(data['market_sessions'])}")
            
            # Show a sample of intraday prices
            intraday = data.get('intraday_prices', [])
            if intraday:
                print(f"\n📋 Sample Intraday Prices (showing first 5):")
                for i, price in enumerate(intraday[:5]):
                    print(f"  {i+1}. {price['time']} - ${price['price']} ({price['market_status']})")
                    
                if len(intraday) > 5:
                    print(f"  ... and {len(intraday) - 5} more entries")
            else:
                print("⚠️  No intraday data available for today")
                
        else:
            print(f"❌ Error: {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error details: {error_data}")
            except:
                print(f"Error response: {response.text}")
                
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
    except json.JSONDecodeError as e:
        print(f"❌ JSON decode error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def test_comparison_with_other_ranges():
    """Compare 1day with other ranges to show the difference"""
    print(f"\n🔄 Comparing different time ranges for {TEST_SYMBOL}")
    print("=" * 50)
    
    ranges = ["1day", "1month"]
    
    for range_param in ranges:
        print(f"\n📊 Testing range: {range_param}")
        url = f"{BASE_URL}/historical/{TEST_SYMBOL}/"
        params = {"range": range_param}
        
        try:
            response = requests.get(url, params=params, timeout=30)
            if response.status_code == 200:
                data = response.json()
                if range_param == "1day":
                    print(f"  ✅ {range_param}: {data.get('data_points', 0)} intraday points for {data.get('date', 'today')}")
                else:
                    stock_prices = data.get('stock_prices', [])
                    print(f"  ✅ {range_param}: {len(stock_prices)} daily points")
            else:
                print(f"  ❌ {range_param}: Error {response.status_code}")
        except Exception as e:
            print(f"  ❌ {range_param}: {e}")

if __name__ == "__main__":
    print(f"🚀 Starting 1day endpoint test at {datetime.now()}")
    test_1day_endpoint()
    test_comparison_with_other_ranges()
    print(f"\n✨ Test completed at {datetime.now()}")
