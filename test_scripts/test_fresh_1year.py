import requests
import json

# Test fresh 1-year data
api_key = 'mse_5PFAyspVWQnz33boHidjCIiU2y6aNoEmzZteXzRV'
base_url = 'http://127.0.0.1:8000'
headers = {'X-API-Key': api_key}

print('🔄 Testing Fresh 1-Year Data from MSE')
print('=' * 40)

url = f'{base_url}/api/historical/AIRTEL/'
params = {'range': '1year', 'refresh': 'true'}

print('Forcing fresh scrape from MSE website...')
try:
    response = requests.get(url, headers=headers, params=params, timeout=60)
    
    if response.status_code == 200:
        data = response.json()
        data_points = data.get('data_points', 0)
        source = data.get('source', 'unknown')
        
        print(f'✅ Success!')
        print(f'Data points: {data_points}')
        print(f'Source: {source}')
        
        stock_prices = data.get('stock_prices', [])
        if stock_prices:
            first_date = stock_prices[0].get('date')
            last_date = stock_prices[-1].get('date')
            print(f'Date range: {first_date} to {last_date}')
            
            if data_points > 200:
                print(f'✅ Good: {data_points} data points - sufficient for 1 year')
            else:
                print(f'⚠️  Only {data_points} data points - MSE website may not have full 1-year history')
        else:
            print('❌ No stock prices in response')
    else:
        print(f'❌ Error: {response.status_code}')
        print(f'Response: {response.text[:300]}')
        
except Exception as e:
    print(f'❌ Exception: {str(e)}')
