#!/usr/bin/env python3
"""
Debug script to see the actual response structure
"""
import requests
import json

# Test configuration
BASE_URL = "http://localhost:8000/api"
TEST_SYMBOL = "AIRTEL"
API_KEY = "mse_5PFAyspVWQnz33boHidjCIiU2y6aNoEmzZteXzRV"

HEADERS = {
    'X-API-Key': API_KEY,
    'Content-Type': 'application/json'
}

def debug_1day_response():
    """Debug the actual response from 1day endpoint"""
    url = f"{BASE_URL}/historical/{TEST_SYMBOL}/"
    params = {"range": "1day"}
    
    try:
        response = requests.get(url, params=params, headers=HEADERS, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print("🔍 Full Response Structure:")
            print("=" * 50)
            print(json.dumps(data, indent=2, default=str))
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    debug_1day_response()
