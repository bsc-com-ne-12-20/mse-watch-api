# MSE Watch API - Getting Started with API Keys

## 🚀 Quick Start Guide

### 1. Create Your Account
1. Visit http://127.0.0.1:8001/signup/
2. Fill in your details and create an account
3. You'll automatically get a **Free Plan** with 100 API calls per month

### 2. Generate Your API Key
1. Log into your dashboard at http://127.0.0.1:8001/dashboard/
2. Click "Create New Key" in the API Keys section
3. Give your key a descriptive name (e.g., "My App Production")
4. Copy and securely store your API key - it starts with `mse_`

### 3. Make Your First API Call

```bash
# Using curl
curl -H "X-API-Key: your_api_key_here" \
     http://127.0.0.1:8001/api/market-status/
```

```python
# Using Python requests
import requests

headers = {'X-API-Key': 'your_api_key_here'}
response = requests.get('http://127.0.0.1:8001/api/market-status/', headers=headers)
print(response.json())
```

```javascript
// Using JavaScript fetch
fetch('http://127.0.0.1:8001/api/market-status/', {
  headers: {
    'X-API-Key': 'your_api_key_here'
  }
})
.then(response => response.json())
.then(data => console.log(data));
```

## 📊 Available Endpoints

| Endpoint | Description | Example |
|----------|-------------|---------|
| `/api/market-status/` | Current market status | Market open/closed |
| `/api/companies/` | List of all companies | Company symbols & names |
| `/api/latest/` | Latest stock prices | Current prices for all stocks |
| `/api/company/{symbol}/` | Company details | Get data for specific company |
| `/api/historical/{symbol}/` | **Historical prices** | **Price history with smart caching** |

## 📈 Historical Data Endpoint (Featured)

### **GET** `/api/historical/{symbol}/`

Get historical stock price data for any MSE-listed company with intelligent caching for optimal performance.

#### **Path Parameters:**
- `symbol` (string, required): Stock symbol (e.g., AIRTEL, TNM, NBM)

#### **Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `range` | string | `1month` | Time range for historical data |
| `cache` | boolean | `true` | Whether to use cached data |
| `refresh` | boolean | `false` | Force refresh from source |

#### **Supported Time Ranges:**
- `1day` - **🆕 Intraday data** (real-time price movements throughout the trading day)
- `1month` - Last 30 days
- `3months` - Last 90 days  
- `6months` - Last 180 days
- `1year` - Last 12 months
- `2years` - Last 24 months
- `5years` - Last 60 months

> **📊 NEW: Intraday Data Available!**  
> Use `range=1day` to get real-time intraday price movements with market session identification.  
> **[📖 View Detailed Intraday API Documentation →](INTRADAY_API_GUIDE.md)**

#### **Supported Companies (16 Total):**
| Symbol | Company Name | ID |
|--------|-------------|-----|
| AIRTEL | Airtel Malawi PLC | MWAIRT001156 |
| TNM | Telekom Networks Malawi PLC | MWTNM0010126 |
| NBM | National Bank of Malawi | MWNBM0010074 |
| STANDARD | Standard Bank Malawi PLC | MWSTD0010041 |
| BHL | Blantyre Hotels Limited | MWBHL0010029 |
| FDHB | FDH Bank Limited | MWFDHB001166 |
| FMBCH | FMB Capital Holdings PLC | MWFMB0010138 |
| ICON | Icon PLC | MWICON001146 |
| ILLOVO | Illovo Sugar Malawi PLC | MWILLV010032 |
| MPICO | MPICO PLC | MWMPI0010116 |
| NBS | NBS Bank PLC | MWNBS0010105 |
| NICO | NICO Holdings PLC | MWNICO010014 |
| NITL | National Investment Trust Limited | MWNITL010091 |
| OMU | Old Mutual PLC | ZAE000255360 |
| PCL | Press Corporation Limited | MWPCL0010053 |
| SUNBIRD | Sunbird Tourism PLC | MWSTL0010085 |

#### **Example Requests:**

```bash
# Get 1 month of AIRTEL data (default)
curl -H "X-API-Key: your_api_key" \
     "http://127.0.0.1:8000/api/historical/AIRTEL/"

# Get 3 months of TNM data
curl -H "X-API-Key: your_api_key" \
     "http://127.0.0.1:8000/api/historical/TNM/?range=3months"

# Force refresh NBM data (bypass cache)
curl -H "X-API-Key: your_api_key" \
     "http://127.0.0.1:8000/api/historical/NBM/?refresh=true"

# Get 1 year of STANDARD data without cache
curl -H "X-API-Key: your_api_key" \
     "http://127.0.0.1:8000/api/historical/STANDARD/?range=1year&cache=false"
```

#### **Python Examples:**

```python
import requests

headers = {'X-API-Key': 'your_api_key_here'}
base_url = 'http://127.0.0.1:8000'

# Get 1 month AIRTEL data
response = requests.get(f'{base_url}/api/historical/AIRTEL/', headers=headers)
data = response.json()

# Get 6 months TNM data
params = {'range': '6months'}
response = requests.get(f'{base_url}/api/historical/TNM/', headers=headers, params=params)
data = response.json()

# Force refresh STANDARD data
params = {'range': '1year', 'refresh': 'true'}
response = requests.get(f'{base_url}/api/historical/STANDARD/', headers=headers, params=params)
data = response.json()
```

#### **JavaScript Examples:**

```javascript
const apiKey = 'your_api_key_here';
const baseUrl = 'http://127.0.0.1:8000';
const headers = { 'X-API-Key': apiKey };

// Get 1 month AIRTEL data
fetch(`${baseUrl}/api/historical/AIRTEL/`, { headers })
  .then(response => response.json())
  .then(data => console.log(data));

// Get 3 months TNM data
fetch(`${baseUrl}/api/historical/TNM/?range=3months`, { headers })
  .then(response => response.json())
  .then(data => console.log(data));

// Force refresh NBM data
fetch(`${baseUrl}/api/historical/NBM/?refresh=true`, { headers })
  .then(response => response.json())
  .then(data => console.log(data));
```

#### **Response Format:**

```json
{
  "company": {
    "symbol": "AIRTEL",
    "name": "Airtel Malawi PLC"
  },
  "time_range": "1month",
  "data_points": 22,
  "source": "cache",
  "retrieved_at": "2025-06-21T20:00:00.000000",
  "stock_prices": [
    {
      "date": "2025-05-21",
      "price": 127.98,
      "close": 127.98,
      "open": null,
      "high": null,
      "low": null,
      "volume": null,
      "turnover": null
    },
    {
      "date": "2025-05-22", 
      "price": 127.97,
      "close": 127.97,
      "open": null,
      "high": null,
      "low": null,
      "volume": null,
      "turnover": null
    }
    // ... more data points
  ]
}
```

#### **Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `company.symbol` | string | Stock symbol |
| `company.name` | string | Full company name |
| `time_range` | string | Requested time range |
| `data_points` | integer | Number of price data points |
| `source` | string | Data source (`cache` or `mse.co.mw`) |
| `retrieved_at` | string | ISO timestamp of data retrieval |
| `stock_prices` | array | Array of historical price data |
| `stock_prices[].date` | string | Date in YYYY-MM-DD format |
| `stock_prices[].price` | float | Stock price (same as close) |
| `stock_prices[].close` | float | Closing price |
| `stock_prices[].open` | float | Opening price (may be null) |
| `stock_prices[].high` | float | Highest price (may be null) |
| `stock_prices[].low` | float | Lowest price (may be null) |
| `stock_prices[].volume` | integer | Trading volume (may be null) |
| `stock_prices[].turnover` | float | Trading turnover (may be null) |

#### **Performance & Caching:**

- **Cached Data**: ~30-50ms response time ⚡
- **Fresh Data**: ~2-3 seconds response time 🔄
- **Cache Duration**: 6 hours for recent data, 24 hours for older data
- **Auto-refresh**: Daily cache invalidation at market close

#### **Error Responses:**

```json
// Company not found or unsupported
{
  "error": "Could not retrieve historical data for XYZ",
  "message": "Data may not be available for this symbol or time range"
}

// Invalid time range
{
  "error": "Invalid time range specified",
  "valid_ranges": ["1month", "3months", "6months", "1year", "2years", "5years"]
}
```

## 🔧 Authentication

All API requests require authentication using an API key:

### Headers Required:
```
X-API-Key: mse_your_40_character_api_key_here
```

### Alternative (Authorization header):
```
Authorization: Bearer mse_your_40_character_api_key_here
```

## 📈 Usage Limits

### Free Plan (Current)
- ✅ **100 requests/month**
- ✅ **Up to 1 API key**
- ✅ **All endpoints available**
- ✅ **Community support**

### Developer Plan (Coming Soon)
- 🚀 **50,000 requests/month**
- 🚀 **Up to 20 API keys**
- 🚀 **Priority support**
- 🚀 **Advanced analytics**

### Business Plan (Coming Soon)
- 💼 **500,000 requests/month**
- 💼 **Unlimited API keys**
- 💼 **Dedicated support**
- 💼 **Custom integrations**

## 🛡️ Security Best Practices

1. **Keep your API key secret** - Never commit it to version control
2. **Use environment variables** - Store keys in `.env` files
3. **Rotate keys regularly** - Create new keys and delete old ones
4. **Monitor usage** - Check your dashboard for unusual activity
5. **Use descriptive names** - Name your keys by their purpose

## ❌ Error Codes

| Code | Error | Description |
|------|-------|-------------|
| 401 | `API key required` | Missing X-API-Key header |
| 401 | `Invalid API key` | Key not found or inactive |
| 403 | `Subscription inactive` | Account subscription issues |
| 429 | `Quota exceeded` | Monthly limit reached |

## 🔍 Example Response

```json
{
  "symbol": "NBM",
  "company_name": "National Bank of Malawi",
  "price": 850.00,
  "change": 25.00,
  "change_percent": 3.03,
  "volume": 1250,
  "date": "2025-06-16",
  "time": "14:30:00"
}
```

## 🆘 Need Help?

- **Dashboard**: Monitor your usage and manage keys
- **API Documentation**: Visit `/swagger/` for interactive docs  
- **Support**: Contact us through the dashboard
- **Status**: Check your quotas and billing in the dashboard

## 🔧 Testing Tools

We've included a test script to help you get started:

```bash
python test_api_client.py
```

This script will guide you through testing all major endpoints with your API key.

---

**Ready to build? Your Malawi Stock Exchange data is just an API call away! 📈**
