# Historical Data Endpoint Reference

## **Endpoint Overview**

The Historical Data API provides access to historical stock price data for all 16 companies listed on the Malawi Stock Exchange (MSE). This endpoint features intelligent caching, multiple time ranges, and real-time data scraping from the official MSE website.

---

## **URL**
```
GET /api/historical/{symbol}/
```

---

## **Required Parameters**

### Path Parameters
| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `symbol` | string | ✅ **Yes** | Stock symbol (case-insensitive) | `AIRTEL`, `TNM`, `NBM` |

### Headers
| Header | Required | Description | Example |
|--------|----------|-------------|---------|
| `X-API-Key` | ✅ **Yes** | Your API authentication key | `mse_your_40_character_api_key_here` |

---

## **Optional Query Parameters**
| Parameter | Type | Default | Description | Valid Values |
|-----------|------|---------|-------------|--------------|
| `range` | string | `1month` | Time range for historical data | `1month`, `3months`, `6months`, `1year`, `2years`, `5years` |
| `cache` | boolean | `true` | Whether to use cached data | `true`, `false` |
| `refresh` | boolean | `false` | Force refresh from source | `true`, `false` |

---

## **Supported Stock Symbols (16 Total)**

| Symbol | Company Name | MSE ID |
|--------|-------------|--------|
| `AIRTEL` | Airtel Malawi PLC | MWAIRT001156 |
| `TNM` | Telekom Networks Malawi PLC | MWTNM0010126 |
| `NBM` | National Bank of Malawi | MWNBM0010074 |
| `STANDARD` | Standard Bank Malawi PLC | MWSTD0010041 |
| `BHL` | Blantyre Hotels Limited | MWBHL0010029 |
| `FDHB` | FDH Bank Limited | MWFDHB001166 |
| `FMBCH` | FMB Capital Holdings PLC | MWFMB0010138 |
| `ICON` | Icon PLC | MWICON001146 |
| `ILLOVO` | Illovo Sugar Malawi PLC | MWILLV010032 |
| `MPICO` | MPICO PLC | MWMPI0010116 |
| `NBS` | NBS Bank PLC | MWNBS0010105 |
| `NICO` | NICO Holdings PLC | MWNICO010014 |
| `NITL` | National Investment Trust Limited | MWNITL010091 |
| `OMU` | Old Mutual PLC | ZAE000255360 |
| `PCL` | Press Corporation Limited | MWPCL0010053 |
| `SUNBIRD` | Sunbird Tourism PLC | MWSTL0010085 |

---

## **Example Requests**

### Basic Request (1 month of AIRTEL data)
```bash
curl -H "X-API-Key: your_api_key" \
     "http://127.0.0.1:8000/api/historical/AIRTEL/"
```

### Custom Time Range (3 months of TNM data)
```bash
curl -H "X-API-Key: your_api_key" \
     "http://127.0.0.1:8000/api/historical/TNM/?range=3months"
```

### Force Refresh (bypass cache)
```bash
curl -H "X-API-Key: your_api_key" \
     "http://127.0.0.1:8000/api/historical/NBM/?refresh=true"
```

### Combined Parameters
```bash
curl -H "X-API-Key: your_api_key" \
     "http://127.0.0.1:8000/api/historical/STANDARD/?range=1year&cache=false"
```

---

## **Code Examples**

### Python
```python
import requests

headers = {'X-API-Key': 'your_api_key_here'}
base_url = 'http://127.0.0.1:8000'

# Basic request
response = requests.get(f'{base_url}/api/historical/AIRTEL/', headers=headers)
data = response.json()

# With parameters
params = {'range': '6months', 'refresh': 'true'}
response = requests.get(f'{base_url}/api/historical/TNM/', headers=headers, params=params)
data = response.json()

print(f"Retrieved {data['data_points']} data points for {data['company']['name']}")
```

### JavaScript
```javascript
const apiKey = 'your_api_key_here';
const baseUrl = 'http://127.0.0.1:8000';

// Basic request
fetch(`${baseUrl}/api/historical/AIRTEL/`, {
  headers: { 'X-API-Key': apiKey }
})
.then(response => response.json())
.then(data => console.log(data));

// With parameters
fetch(`${baseUrl}/api/historical/TNM/?range=3months&refresh=true`, {
  headers: { 'X-API-Key': apiKey }
})
.then(response => response.json())
.then(data => console.log(`${data.data_points} data points retrieved`));
```

### PHP
```php
<?php
$apiKey = 'your_api_key_here';
$baseUrl = 'http://127.0.0.1:8000';

$headers = [
    'X-API-Key: ' . $apiKey,
    'Content-Type: application/json'
];

// Basic request
$url = $baseUrl . '/api/historical/AIRTEL/';
$ch = curl_init();
curl_setopt($ch, CURLOPT_URL, $url);
curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
$response = curl_exec($ch);
curl_close($ch);

$data = json_decode($response, true);
echo "Retrieved " . $data['data_points'] . " data points\n";
?>
```

---

## **Response Format**

### Success Response (200 OK)
```json
{
  "company": {
    "symbol": "AIRTEL",
    "name": "Airtel Malawi PLC",
    "current_price": 127.98,
    "listing_date": "2015-11-23",
    "listing_price": 100.0,
    "market_cap": null,
    "shares_in_issue": 1000000000
  },
  "time_range": "1year",
  "data_points": 119,
  "source": "cache",
  "retrieved_at": "2025-06-21T14:30:00.000000",
  "data_limitation": "Limited data available: 119 points (expected ~240)",
  "note": "MSE website may not have complete historical data for this time range",
  "stock_prices": [
    {
      "date": "2024-12-23",
      "price": 127.98,
      "close": 127.98,
      "open": null,
      "high": null,
      "low": null,
      "volume": null,
      "turnover": null
    },
    {
      "date": "2024-12-24",
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

**📋 Response with Limited Data**

When the requested time range has insufficient data (e.g., requesting 1 year but only 6 months available), the API will include additional fields:
- `data_limitation`: Description of the limitation
- `note`: Explanation about data availability

This ensures transparency about data completeness.

### Response Fields Description

| Field | Type | Description |
|-------|------|-------------|
| `company.symbol` | string | Stock symbol |
| `company.name` | string | Full company name |
| `company.current_price` | float | Latest available price |
| `company.listing_date` | string | Date company was listed (ISO format) |
| `company.listing_price` | float | Initial listing price |
| `company.shares_in_issue` | integer | Total shares in circulation |
| `time_range` | string | Requested time range |
| `data_points` | integer | Number of price data points returned |
| `source` | string | Data source: `cache` or `mse.co.mw` |
| `retrieved_at` | string | Timestamp when data was retrieved |
| `data_limitation` | string | (Optional) Warning about limited data availability |
| `note` | string | (Optional) Additional information about data limitations |
| `stock_prices` | array | Array of historical price data |
| `stock_prices[].date` | string | Date in YYYY-MM-DD format |
| `stock_prices[].price` | float | Stock price (same as close) |
| `stock_prices[].close` | float | Closing price |
| `stock_prices[].open` | float | Opening price (may be null) |
| `stock_prices[].high` | float | Highest price (may be null) |
| `stock_prices[].low` | float | Lowest price (may be null) |
| `stock_prices[].volume` | integer | Trading volume (may be null) |
| `stock_prices[].turnover` | float | Trading turnover (may be null) |

---

## **Error Responses**

### Invalid Symbol (404 Not Found)
```json
{
  "error": "Could not retrieve historical data for XYZ",
  "message": "Data may not be available for this symbol or time range"
}
```

### Invalid Time Range (400 Bad Request)
```json
{
  "error": "Invalid time range specified",
  "valid_ranges": ["1month", "3months", "6months", "1year", "2years", "5years"]
}
```

### Authentication Error (401 Unauthorized)
```json
{
  "error": "API key required",
  "message": "Please provide a valid API key in the X-API-Key header"
}
```

### Rate Limit Exceeded (429 Too Many Requests)
```json
{
  "error": "Quota exceeded",
  "message": "Monthly API call limit reached. Upgrade your plan for more requests."
}
```

---

## **Performance & Caching**

### Performance Metrics
- **Cached Response**: ~30-50ms ⚡
- **Fresh Data**: ~2-3 seconds 🔄
- **Cache Duration**: 6-24 hours depending on data age
- **Daily Refresh**: Automatic cache invalidation

### Data Points by Time Range
| Range | Approximate Data Points | Description | Current Status |
|-------|------------------------|-------------|----------------|
| `1month` | ~22 points | Last 30 days | ✅ Full data available |
| `3months` | ~60 points | Last 90 days | ✅ Full data available |
| `6months` | ~120 points | Last 180 days | ✅ Full data available |
| `1year` | ~240 points | Last 12 months | ⚠️ **Limited data (~119 points)** |
| `2years` | ~480 points | Last 24 months | ⚠️ **Limited data (~119 points)** |
| `5years` | ~1200 points | Last 60 months | ⚠️ **Limited data (~119 points)** |

**📊 Data Availability Note**: Currently, the MSE website has historical data going back to approximately December 2024. This means that requests for 1year, 2years, and 5years will return the same limited dataset until more historical data becomes available from the source.

### Caching Strategy
- **Memory Cache**: Fast in-memory caching for recent requests
- **Database Cache**: Persistent storage for historical data
- **Smart Refresh**: Automatic refresh based on market hours and data age
- **Force Refresh**: Use `refresh=true` to bypass cache and get fresh data

---

## **Data Limitations & Transparency**

### Current Data Availability
- **Historical Data Range**: December 2024 - Present (~6 months)
- **Full Data Available**: 1month, 3months, 6months
- **Limited Data**: 1year, 2years, 5years (returns ~119 data points)

### Automatic Detection
The API automatically detects when requested data exceeds availability and includes:
- `data_limitation` field: Describes the limitation
- `note` field: Explains the cause
- Transparent data point counts

### Future Improvements
As the MSE website accumulates more historical data over time, longer time ranges will automatically return more complete datasets without any code changes required.

---

## **Best Practices**

### 1. **Use Caching Effectively**
- Default caching provides optimal performance
- Only use `refresh=true` when you need the latest data
- Cache is automatically refreshed daily

### 2. **Handle Rate Limits**
- Monitor your API usage in the dashboard
- Implement exponential backoff for rate limit errors
- Consider upgrading your plan for higher limits

### 3. **Error Handling**
```python
import requests
from time import sleep

def get_historical_data(symbol, range_param='1month', max_retries=3):
    headers = {'X-API-Key': 'your_api_key'}
    url = f'http://127.0.0.1:8000/api/historical/{symbol}/'
    params = {'range': range_param}
    
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=headers, params=params, timeout=30)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:
                # Rate limited, wait and retry
                sleep(2 ** attempt)
                continue
            else:
                print(f"Error: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            if attempt < max_retries - 1:
                sleep(1)
            
    return None
```

### 4. **Optimize for Your Use Case**
- Use appropriate time ranges for your analysis
- Combine multiple requests efficiently
- Cache responses locally if making repeated requests

---

## **Testing**

### Test the Endpoint
```bash
# Test basic functionality
curl -H "X-API-Key: your_api_key" \
     "http://127.0.0.1:8000/api/historical/AIRTEL/" | jq

# Test different time ranges
curl -H "X-API-Key: your_api_key" \
     "http://127.0.0.1:8000/api/historical/TNM/?range=3months" | jq

# Test cache performance
time curl -H "X-API-Key: your_api_key" \
          "http://127.0.0.1:8000/api/historical/NBM/"
```

---

## **Support**

For additional help:
- **Dashboard**: Monitor usage at `/dashboard/`
- **Interactive Docs**: Visit `/swagger/` for API explorer
- **Support**: Contact through the dashboard
- **Status**: Check system status and your quotas

---

**📈 Ready to analyze MSE historical data? Start with a simple request and explore the rich dataset available through this endpoint!**
