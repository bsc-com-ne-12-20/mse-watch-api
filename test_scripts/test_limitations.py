import requests
import json

def test_limitation_warnings():
    """Test if limitation warnings are working"""
    base_url = "http://127.0.0.1:8000"
    api_key = "mse_5PFAyspVWQnz33boHidjCIiU2y6aNoEmzZteXzRV"
    
    headers = {
        'X-API-Key': api_key,
        'Content-Type': 'application/json'
    }
    
    print("🔍 Testing Data Limitation Warnings")
    print("=" * 50)
    
    # Test 1 year and 2 years to see if warnings appear
    test_cases = [
        {'range': '1year', 'expected': 240},
        {'range': '2years', 'expected': 480}
    ]
    
    for test in test_cases:
        print(f"\n📊 Testing {test['range']} (expected ~{test['expected']} points)")
        
        url = f"{base_url}/api/historical/AIRTEL/"
        params = {'range': test['range']}
        
        try:
            response = requests.get(url, params=params, headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                data_points = data.get('data_points', 0)
                
                print(f"   ✅ Status: 200 OK")
                print(f"   📊 Data points: {data_points}")
                print(f"   📈 Expected: ~{test['expected']}")
                
                # Check for limitation warnings
                if 'data_limitation' in data:
                    print(f"   ⚠️  Data limitation: {data['data_limitation']}")
                else:
                    print(f"   ✅ No limitation warning")
                    
                if 'note' in data:
                    print(f"   📝 Note: {data['note']}")
                    
                # Check if warning should have appeared
                if data_points < test['expected'] * 0.7:
                    if 'data_limitation' not in data:
                        print(f"   ❌ WARNING: Should have data limitation warning!")
                    else:
                        print(f"   ✅ Correctly detected data limitation")
                else:
                    print(f"   ✅ Sufficient data, no warning needed")
                    
            else:
                print(f"   ❌ Error: {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                
        except Exception as e:
            print(f"   ❌ Exception: {str(e)}")

if __name__ == "__main__":
    test_limitation_warnings()
