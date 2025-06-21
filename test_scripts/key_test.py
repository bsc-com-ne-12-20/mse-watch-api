import requests

# Your API key from the dashboard
api_key = "mse_KTHrv62tXf9IYyuN2vE1DBY9QuXgd9n0R6aHTG6C"

headers = {
    'X-API-Key': api_key
}

# Use the correct port 8002
response = requests.get('http://127.0.0.1:8000/api/historical/NBM/?range=1month', headers=headers)

if response.status_code == 200:
    data = response.json()
    print(data)
    print("✅ Success!")
    print(f"Got {len(data)} stock prices")
#     for stock in data[:16]:  # Show first 16
#         print(f"  {stock['symbol']}: {stock['price']}")
# else:
#     print(f"❌ Error {response.status_code}: {response.text}")