#!/usr/bin/env python3
"""
Test script for the public stock icon API endpoint

This script tests the stock icon endpoint without requiring authentication.
"""

import requests
import os

def test_stock_icon_api():
    """Test the stock icon API endpoint"""
    base_url = "http://127.0.0.1:8000"
    
    print("🎨 Testing Stock Icon API")
    print("=" * 50)
    
    # First, test the list endpoint
    print(f"\n📋 Testing stock icons list...")
    try:
        response = requests.get(f"{base_url}/api/stock-icons/")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Successfully got icons list")
            print(f"   Total icons: {data.get('total_icons', 0)}")
            print(f"   Supported formats: {data.get('supported_formats', [])}")
            
            # Use the actual available symbols from the API
            available_icons = data.get('available_icons', [])
            test_symbols = [icon['symbol'] for icon in available_icons[:5]]  # Test first 5
            
            if available_icons:
                print(f"   Sample icons: {[icon['symbol'] for icon in available_icons[:3]]}")
        else:
            print(f"❌ Error getting icons list: {response.status_code}")
            # Fallback to predefined symbols
            test_symbols = ["AIRTEL", "TNM", "FCB", "STANDARD", "SUNBIRD"]
            
    except Exception as e:
        print(f"❌ Error testing icons list: {e}")
        test_symbols = ["AIRTEL", "TNM", "FCB", "STANDARD", "SUNBIRD"]
    
    # Test individual icons
    for symbol in test_symbols:
        print(f"\n📷 Testing icon for {symbol}...")
        
        try:
            response = requests.get(f"{base_url}/api/stock-icon/{symbol}/")
            
            if response.status_code == 200:
                content_type = response.headers.get('content-type', 'unknown')
                content_length = len(response.content)
                
                print(f"✅ Success!")
                print(f"   Content-Type: {content_type}")
                print(f"   Size: {content_length} bytes")
                
                # Optionally save the image for verification
                extension = 'png' if 'png' in content_type else 'jpg'
                filename = f"test_{symbol.lower()}_icon.{extension}"
                with open(filename, 'wb') as f:
                    f.write(response.content)
                print(f"   Saved as: {filename}")
                
            elif response.status_code == 404:
                print(f"❌ Image not found for {symbol}")
            else:
                print(f"❌ Error {response.status_code}: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print(f"\n🔍 Testing invalid symbol...")
    try:
        response = requests.get(f"{base_url}/api/stock-icon/INVALID/")
        if response.status_code == 404:
            print(f"✅ Correctly returned 404 for invalid symbol")
        else:
            print(f"❌ Unexpected response for invalid symbol: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing invalid symbol: {e}")
    
    print(f"\n✨ Test completed!")
    print(f"\n💡 Usage:")
    print(f"   GET {base_url}/api/stock-icons/")
    print(f"   GET {base_url}/api/stock-icon/SYMBOL/")
    print(f"   - No authentication required")
    print(f"   - Returns image file directly")
    print(f"   - Supports PNG, JPEG, JPG formats")
    print(f"   - Case insensitive symbol matching")
    print(f"   - CORS enabled for web usage")

if __name__ == "__main__":
    test_stock_icon_api()
