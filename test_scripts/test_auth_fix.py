#!/usr/bin/env python3
"""
Quick test to verify the authentication fix
"""

import requests

def test_auth_fix():
    """Test that endpoints correctly require authentication"""
    base_url = "http://127.0.0.1:8000"
    
    print("🔧 Testing Authentication Fix")
    print("=" * 40)
    
    # Test endpoints that should require API key
    endpoints = [
        "/api/market-status/",
        "/api/companies/",
        "/api/latest/",
    ]
    
    print("\n🔐 Testing WITHOUT API Key (should return 401):")
    for endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}")
            status = "✅ PROTECTED" if response.status_code == 401 else f"❌ NOT PROTECTED ({response.status_code})"
            print(f"   {endpoint}: {status}")
            
            if response.status_code == 401:
                try:
                    data = response.json()
                    print(f"      Message: {data.get('message', 'No message')}")
                except:
                    print(f"      Response: {response.text[:100]}")
        except Exception as e:
            print(f"   {endpoint}: ❌ ERROR - {e}")
    
    print("\n📖 Testing Public Endpoints (should work):")
    public_endpoints = [
        "/api/stock-icons/",
        "/api/stock-icon/TNM/",
    ]
    
    for endpoint in public_endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}")
            status = "✅ PUBLIC" if response.status_code in [200, 404] else f"❌ ERROR ({response.status_code})"
            print(f"   {endpoint}: {status}")
        except Exception as e:
            print(f"   {endpoint}: ❌ ERROR - {e}")
    
    print(f"\n✨ Test Complete!")
    print(f"\nExpected Results:")
    print(f"  - Protected endpoints should return 401 without API key")
    print(f"  - Public endpoints should return 200 or 404 (not 401)")

if __name__ == "__main__":
    test_auth_fix()
