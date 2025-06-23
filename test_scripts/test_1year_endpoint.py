import requests
import json

def test_1year_endpoint():
    """Test the 1 year endpoint specifically"""
    base_url = "http://127.0.0.1:8000"
    api_key = "mse_5PFAyspVWQnz33boHidjCIiU2y6aNoEmzZteXzRV"
    
    headers = {
        'X-API-Key': api_key,
        'Content-Type': 'application/json'
    }
    
    print("🔍 Testing 1 Year Endpoint Data Points")
    print("=" * 50)
    
    # Test different time ranges for comparison
    time_ranges = ['1month', '3months', '6months', '1year', '2years']
    symbol = 'AIRTEL'
    
    for time_range in time_ranges:
        print(f"\n📊 Testing {symbol} - {time_range}")
        
        url = f"{base_url}/api/historical/{symbol}/"
        params = {'range': time_range}
        
        try:
            response = requests.get(url, params=params, headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                data_points = data.get('data_points', 0)
                source = data.get('source', 'unknown')
                
                stock_prices = data.get('stock_prices', [])
                if stock_prices:
                    first_date = stock_prices[0].get('date', 'unknown')
                    last_date = stock_prices[-1].get('date', 'unknown')
                    
                    print(f"   ✅ Success!")
                    print(f"   Data points: {data_points}")
                    print(f"   Source: {source}")
                    print(f"   Date range: {first_date} to {last_date}")
                    
                    # Calculate expected vs actual
                    if time_range == '1month':
                        expected = "~22"
                    elif time_range == '3months':
                        expected = "~60"
                    elif time_range == '6months':
                        expected = "~120"
                    elif time_range == '1year':
                        expected = "~240"
                    elif time_range == '2years':
                        expected = "~480"
                    else:
                        expected = "unknown"
                        
                    print(f"   Expected: {expected} | Actual: {data_points}")
                    
                    if time_range == '1year' and data_points < 200:
                        print(f"   ⚠️  WARNING: 1 year data seems low ({data_points} < 200)")
                        
                else:
                    print(f"   ❌ No stock prices data")
                    
            else:
                print(f"   ❌ Error: {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                
        except Exception as e:
            print(f"   ❌ Exception: {str(e)}")

if __name__ == "__main__":
    test_1year_endpoint()
