#!/usr/bin/env python3
"""
MSE Watch API - Test Script for API Key Authentication

This script demonstrates how to:
1. Create an API key through the dashboard
2. Use the API key to make authenticated requests
3. Monitor usage and quotas

Requirements:
- An active MSE Watch account (free plan works)
- An API key created through the dashboard
"""

import requests
import json
import time


class MSEWatchAPIClient:
    """Simple client for MSE Watch API"""
    
    def __init__(self, api_key, base_url="http://127.0.0.1:8000"):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            'X-API-Key': api_key,
            'Content-Type': 'application/json'
        }
    
    def get_market_status(self):
        """Get current market status"""
        response = requests.get(f"{self.base_url}/api/market-status/", headers=self.headers)
        return response.json() if response.status_code == 200 else response.text
    
    def get_companies(self):
        """Get list of companies"""
        response = requests.get(f"{self.base_url}/api/companies/", headers=self.headers)
        return response.json() if response.status_code == 200 else response.text
    
    def get_latest_prices(self):
        """Get latest stock prices"""
        response = requests.get(f"{self.base_url}/api/latest/", headers=self.headers)
        return response.json() if response.status_code == 200 else response.text
    
    def get_company_detail(self, symbol):
        """Get details for a specific company"""
        response = requests.get(f"{self.base_url}/api/company/{symbol}/", headers=self.headers)
        return response.json() if response.status_code == 200 else response.text


def main():
    print("🚀 MSE Watch API Test Client")
    print("=" * 50)
    
    # You'll need to replace this with your actual API key from the dashboard
    api_key = input("Enter your API key (from MSE Watch dashboard): ").strip()
    
    if not api_key:
        print("❌ API key is required!")
        return
    
    # Initialize client
    client = MSEWatchAPIClient(api_key)
    
    print(f"\n📡 Testing API with key: {api_key[:8]}...")
    
    # Test endpoints
    tests = [
        ("Market Status", client.get_market_status),
        ("Companies List", client.get_companies),
        ("Latest Prices", client.get_latest_prices),
    ]
    
    for test_name, test_func in tests:
        print(f"\n🔍 Testing {test_name}...")
        try:
            result = test_func()
            if isinstance(result, dict) and 'error' in result:
                print(f"❌ Error: {result['error']} - {result.get('message', '')}")
            else:
                print(f"✅ Success! Got {len(result) if isinstance(result, list) else 'data'}")
                if isinstance(result, list) and len(result) > 0:
                    print(f"   Sample: {result[0] if result else 'No data'}")
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        time.sleep(0.5)  # Small delay between requests
    
    print(f"\n✨ Test completed!")
    print(f"\n💡 Tips:")
    print(f"   • Free plan: 100 requests/month")
    print(f"   • Monitor usage in your dashboard")
    print(f"   • API key format: mse_[40 characters]")
    print(f"   • Use X-API-Key header for authentication")


if __name__ == "__main__":
    main()
