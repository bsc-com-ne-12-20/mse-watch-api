#!/usr/bin/env python3
"""
Direct test of the historical service
"""
import os
import sys
import django

# Add the project root directory to the Python path
sys.path.append('/mnt/c/Users/innow/OneDrive/Desktop/mse_api')

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from stocks.services.historical_service import MSEHistoricalService

def test_service_directly():
    """Test the historical service directly"""
    service = MSEHistoricalService()
    
    print("🧪 Testing MSEHistoricalService directly")
    print("=" * 50)
    
    # Test 1day range
    print("📊 Testing 1day range...")
    result = service.get_historical_data("AIRTEL", "1day")
    
    if result:
        print("✅ Service returned data")
        print(f"📋 Keys in result: {list(result.keys())}")
        
        if 'symbol' in result:
            print(f"📈 Symbol: {result['symbol']}")
        if 'date' in result:
            print(f"📅 Date: {result['date']}")
        if 'intraday_prices' in result:
            print(f"💰 Intraday prices: {len(result.get('intraday_prices', []))} entries")
        if 'data_points' in result:
            print(f"📊 Data points: {result['data_points']}")
    else:
        print("❌ Service returned None")
    
    # Test intraday method directly
    print("\n🔍 Testing get_intraday_data directly...")
    intraday_result = service.get_intraday_data("AIRTEL")
    
    if intraday_result:
        print("✅ Intraday method returned data")
        print(f"📋 Keys: {list(intraday_result.keys())}")
    else:
        print("❌ Intraday method returned None")

if __name__ == "__main__":
    test_service_directly()
