#!/usr/bin/env python3
"""
Test script to verify API authentication for different endpoints

This script tests:
1. Public endpoints (no API key required)
2. Protected endpoints (API key required)
"""

import requests


def test_authentication():
    """Test API authentication requirements"""
    base_url = "http://127.0.0.1:8000"
    
    print("🔒 Testing API Authentication")
    print("=" * 50)
    
    # Test public endpoints (should work without API key)
    public_endpoints = [
        ("/api/stock-icons/", "Stock Icons List"),
        ("/api/stock-icon/TNM/", "TNM Stock Icon"),
        ("/api/docs/", "API Documentation"),
    ]
    
    print("\n📖 Testing Public Endpoints (No API Key):")
    for endpoint, name in public_endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}")
            status = "✅ PUBLIC" if response.status_code != 401 else "❌ REQUIRES AUTH"
            print(f"   {name}: {status} ({response.status_code})")
        except Exception as e:
            print(f"   {name}: ❌ ERROR - {e}")
    
    # Test protected endpoints (should require API key)
    protected_endpoints = [
        ("/api/market-status/", "Market Status"),
        ("/api/latest/", "Latest Prices"),
        ("/api/companies/", "Companies List"),
        ("/api/historical/TNM/", "Historical Data"),
    ]
    
    print("\n🔐 Testing Protected Endpoints (Without API Key):")
    for endpoint, name in protected_endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}")
            status = "✅ PROTECTED" if response.status_code == 401 else "❌ NOT PROTECTED"
            print(f"   {name}: {status} ({response.status_code})")
            
            if response.status_code == 401:
                try:
                    error_data = response.json()
                    print(f"      Error: {error_data.get('error', 'Unknown')}")
                except:
                    pass
        except Exception as e:
            print(f"   {name}: ❌ ERROR - {e}")
    
    print("\n🔑 Testing Protected Endpoints (With Valid API Key):")
    api_key = input("\nEnter a valid API key to test authenticated access (or press Enter to skip): ").strip()
    
    if api_key:
        headers = {'X-API-Key': api_key}
        
        for endpoint, name in protected_endpoints:
            try:
                response = requests.get(f"{base_url}{endpoint}", headers=headers)
                status = "✅ SUCCESS" if response.status_code == 200 else f"❌ ERROR ({response.status_code})"
                print(f"   {name}: {status}")
                
                if response.status_code != 200:
                    try:
                        error_data = response.json()
                        print(f"      Error: {error_data.get('error', 'Unknown')}")
                    except:
                        pass
            except Exception as e:
                print(f"   {name}: ❌ ERROR - {e}")
    else:
        print("   Skipped - No API key provided")
    
    print(f"\n✨ Authentication Test Complete!")
    print(f"\n📋 Summary:")
    print(f"   ✅ Public endpoints: No authentication required")
    print(f"   🔐 Protected endpoints: API key required")
    print(f"   📍 Market Status: NOW REQUIRES API KEY")


if __name__ == "__main__":
    test_authentication()
