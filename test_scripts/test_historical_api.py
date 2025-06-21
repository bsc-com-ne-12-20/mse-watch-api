import requests
import json

def test_historical_api():
    """Test the new historical data API"""
    base_url = "http://127.0.0.1:8000"
    api_key = "mse_5PFAyspVWQnz33boHidjCIiU2y6aNoEmzZteXzRV"  # Test API key
    
    headers = {
        'X-API-Key': api_key,
        'Content-Type': 'application/json'
    }
    
    print("🚀 Testing Historical Data API")
    print("=" * 50)
      # Test cases
    test_cases = [
        {
            'symbol': 'AIRTEL',
            'range': '1month',
            'description': 'AIRTEL 1 month data'
        },
        {
            'symbol': 'TNM', 
            'range': '1month',
            'description': 'TNM 1 month data'
        },
        {
            'symbol': 'NBM',
            'range': '1month', 
            'description': 'NBM 1 month data'
        },
        {
            'symbol': 'STANDARD',
            'range': '3months',
            'description': 'STANDARD 3 months data'
        }
    ]
    
    for test in test_cases:
        print(f"\n📊 Testing: {test['description']}")
        
        url = f"{base_url}/api/historical/{test['symbol']}/"
        params = {'range': test['range']}
        
        try:
            response = requests.get(url, params=params, headers=headers, timeout=30)
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Success!")
                print(f"   Data points: {data.get('data_points', 'N/A')}")
                print(f"   Time range: {data.get('time_range', 'N/A')}")
                print(f"   Source: {data.get('source', 'N/A')}")
                print(f"   Company: {data.get('company', {}).get('name', 'N/A')}")
                
                # Show sample data
                stock_prices = data.get('stock_prices', [])
                if stock_prices:
                    print(f"   Sample price: {stock_prices[0].get('date')} = {stock_prices[0].get('price')}")
            else:
                print(f"   ❌ Failed: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Request error: {e}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print(f"\n🔄 Testing cache functionality...")
    print("Making the same request again to test caching...")
    
    # Test caching by making the same request twice
    url = f"{base_url}/api/historical/AIRTEL/"
    params = {'range': '1month'}
    
    try:
        # First request
        start_time = time.time()
        response1 = requests.get(url, params=params, headers=headers, timeout=30)
        first_duration = time.time() - start_time
        
        # Second request (should be cached)
        start_time = time.time() 
        response2 = requests.get(url, params=params, headers=headers, timeout=30)
        second_duration = time.time() - start_time
        
        if response1.status_code == 200 and response2.status_code == 200:
            data1 = response1.json()
            data2 = response2.json()
            
            print(f"   First request: {first_duration:.2f}s (source: {data1.get('source', 'unknown')})")
            print(f"   Second request: {second_duration:.2f}s (source: {data2.get('source', 'unknown')})")
            
            if second_duration < first_duration:
                print(f"   ✅ Caching working! Second request was faster.")
            else:
                print(f"   ⚠️  Cache may not be working optimally.")
        
    except Exception as e:
        print(f"   ❌ Cache test error: {e}")

if __name__ == "__main__":
    import time
    test_historical_api()
