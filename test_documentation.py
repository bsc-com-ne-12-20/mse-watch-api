#!/usr/bin/env python3
"""
Test script to validate the documentation examples work correctly
"""
import requests
import json
from datetime import datetime

# Configuration from documentation
BASE_URL = "http://localhost:8000/api"
API_KEY = "mse_5PFAyspVWQnz33boHidjCIiU2y6aNoEmzZteXzRV"

def test_documentation_examples():
    """Test the examples provided in the documentation"""
    print("🧪 Testing Documentation Examples")
    print("=" * 50)
    
    headers = {
        'X-API-Key': API_KEY,
        'Content-Type': 'application/json'
    }
    
    # Test the main example from docs
    print("📋 Testing: GET /api/historical/AIRTEL/?range=1day")
    
    try:
        response = requests.get(
            f"{BASE_URL}/historical/AIRTEL/",
            params={"range": "1day"},
            headers=headers,
            timeout=30
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            # Validate response structure matches documentation
            expected_fields = [
                'symbol', 'date', 'open', 'high', 'low', 'close',
                'data_points', 'market_sessions', 'intraday_prices'
            ]
            
            print("✅ Response structure validation:")
            for field in expected_fields:
                if field in data:
                    print(f"  ✅ {field}: {type(data[field]).__name__}")
                else:
                    print(f"  ❌ Missing field: {field}")
            
            # Validate intraday price structure
            if 'intraday_prices' in data and data['intraday_prices']:
                first_price = data['intraday_prices'][0]
                expected_price_fields = ['time', 'price', 'change', 'direction', 'market_status']
                
                print("\n✅ Intraday price entry validation:")
                for field in expected_price_fields:
                    if field in first_price:
                        print(f"  ✅ {field}: {first_price[field]} ({type(first_price[field]).__name__})")
                    else:
                        print(f"  ❌ Missing field: {field}")
            
            print(f"\n📊 Summary:")
            print(f"  Symbol: {data.get('symbol')}")
            print(f"  Date: {data.get('date')}")
            print(f"  OHLC: O={data.get('open')} H={data.get('high')} L={data.get('low')} C={data.get('close')}")
            print(f"  Data Points: {data.get('data_points')}")
            print(f"  Market Sessions: {', '.join(data.get('market_sessions', []))}")
            
        else:
            print(f"❌ Request failed: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Error: {e}")

def test_error_scenarios():
    """Test documented error scenarios"""
    print(f"\n🔍 Testing Error Scenarios")
    print("=" * 50)
    
    # Test without API key
    print("📋 Testing: Missing API key (should return 401)")
    try:
        response = requests.get(f"{BASE_URL}/historical/AIRTEL/?range=1day", timeout=10)
        print(f"  Status: {response.status_code} ({'✅' if response.status_code == 401 else '❌'})")
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    # Test invalid symbol
    print("📋 Testing: Invalid symbol (should return 404)")
    headers = {'X-API-Key': API_KEY}
    try:
        response = requests.get(f"{BASE_URL}/historical/INVALID/?range=1day", headers=headers, timeout=10)
        print(f"  Status: {response.status_code} ({'✅' if response.status_code == 404 else '❌'})")
    except Exception as e:
        print(f"  ❌ Error: {e}")

if __name__ == "__main__":
    print(f"🚀 Documentation Validation Test - {datetime.now()}")
    test_documentation_examples()
    test_error_scenarios()
    print(f"\n✨ Validation completed!")
