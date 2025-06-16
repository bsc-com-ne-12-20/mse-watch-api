import requests

# Your API key from the dashboard
api_key = "mse_5PFAyspVWQnz33boHidjCIiU2y6aNoEmzZteXzRV"

headers = {
    'X-API-Key': api_key
}

# Use the correct port 8002
response = requests.get('http://127.0.0.1:8000/api/latest/', headers=headers)

if response.status_code == 200:
    data = response.json()
    print("✅ Success!")
    print(f"Got {len(data)} stock prices")
    for stock in data[:3]:  # Show first 3
        print(f"  {stock['symbol']}: {stock['price']}")
else:
    print(f"❌ Error {response.status_code}: {response.text}")