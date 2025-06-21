# Historical Data API - Complete Guide

## 🏆 Overview

The Historical Data API provides access to historical stock price data for all 16 companies listed on the Malawi Stock Exchange (MSE). This endpoint features intelligent caching, multiple time ranges, and real-time data scraping from the official MSE website.

## 🚀 Quick Start

```bash
# Basic request - Get 1 month of AIRTEL data
curl -H "X-API-Key: your_api_key" \
     "https://your-domain.com/api/historical/AIRTEL/"
```

## 📋 Endpoint Details

**URL**: `/api/historical/{symbol}/`  
**Method**: `GET`  
**Authentication**: Required (API Key)  
**Rate Limit**: Based on your subscription plan  

## 🔧 Parameters

### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `symbol` | string | ✅ Yes | Stock symbol (case-insensitive) |

### Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `range` | string | `1month` | Time range for data |
| `cache` | boolean | `true` | Use cached data when available |
| `refresh` | boolean | `false` | Force refresh from source |

## ⏰ Time Ranges

| Range | Description | Approximate Data Points |
|-------|-------------|------------------------|
| `1month` | Last 30 days | ~22 trading days |
| `3months` | Last 90 days | ~60 trading days |
| `6months` | Last 180 days | ~120 trading days |
| `1year` | Last 12 months | ~240 trading days |
| `2years` | Last 24 months | ~480 trading days |
| `5years` | Last 60 months | ~1200 trading days |

## 🏢 Supported Companies

All 16 MSE-listed companies are supported:

### Major Banks & Financial Services
- **NBM** - National Bank of Malawi
- **STANDARD** - Standard Bank Malawi PLC
- **FDHB** - FDH Bank Limited
- **FMBCH** - FMB Capital Holdings PLC
- **NBS** - NBS Bank PLC
- **NICO** - NICO Holdings PLC

### Telecommunications
- **AIRTEL** - Airtel Malawi PLC
- **TNM** - Telekom Networks Malawi PLC

### Industrial & Manufacturing
- **ILLOVO** - Illovo Sugar Malawi PLC
- **PCL** - Press Corporation Limited
- **MPICO** - MPICO PLC

### Tourism & Hospitality
- **BHL** - Blantyre Hotels Limited
- **SUNBIRD** - Sunbird Tourism PLC

### Technology & Services
- **ICON** - Icon PLC
- **NITL** - National Investment Trust Limited

### International
- **OMU** - Old Mutual PLC

## 📝 Code Examples

### Python - Basic Usage

```python
import requests
import json
from datetime import datetime

class MSEHistoricalAPI:
    def __init__(self, api_key, base_url="https://your-domain.com"):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {'X-API-Key': api_key}
    
    def get_historical_data(self, symbol, time_range="1month", use_cache=True, force_refresh=False):
        """Get historical data for a stock symbol"""
        url = f"{self.base_url}/api/historical/{symbol.upper()}/"
        params = {
            'range': time_range,
            'cache': str(use_cache).lower(),
            'refresh': str(force_refresh).lower()
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API request failed: {e}")
            return None
    
    def get_multiple_stocks(self, symbols, time_range="1month"):
        """Get historical data for multiple stocks"""
        results = {}
        for symbol in symbols:
            print(f"Fetching data for {symbol}...")
            data = self.get_historical_data(symbol, time_range)
            if data:
                results[symbol] = data
        return results

# Usage example
api = MSEHistoricalAPI("your_api_key_here")

# Get AIRTEL data
airtel_data = api.get_historical_data("AIRTEL", "3months")
print(f"AIRTEL: {airtel_data['data_points']} data points")

# Get multiple stocks
bank_stocks = ["NBM", "STANDARD", "FDHB"]
bank_data = api.get_multiple_stocks(bank_stocks, "6months")

# Force refresh for latest data
fresh_data = api.get_historical_data("TNM", "1month", force_refresh=True)
```

### JavaScript/Node.js - Advanced Usage

```javascript
class MSEHistoricalAPI {
    constructor(apiKey, baseUrl = "https://your-domain.com") {
        this.apiKey = apiKey;
        this.baseUrl = baseUrl;
        this.headers = { 'X-API-Key': apiKey };
    }

    async getHistoricalData(symbol, timeRange = "1month", options = {}) {
        const { useCache = true, forceRefresh = false } = options;
        
        const url = `${this.baseUrl}/api/historical/${symbol.toUpperCase()}/`;
        const params = new URLSearchParams({
            range: timeRange,
            cache: useCache.toString(),
            refresh: forceRefresh.toString()
        });

        try {
            const response = await fetch(`${url}?${params}`, {
                headers: this.headers
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error(`API request failed: ${error.message}`);
            return null;
        }
    }

    async getPortfolioData(portfolio) {
        const results = {};
        
        for (const [symbol, allocation] of Object.entries(portfolio)) {
            console.log(`Fetching ${symbol} (${allocation}% allocation)...`);
            const data = await this.getHistoricalData(symbol, "1year");
            
            if (data) {
                results[symbol] = {
                    ...data,
                    allocation: allocation
                };
            }
        }
        
        return results;
    }

    calculateReturns(priceData) {
        const prices = priceData.stock_prices.map(p => p.price);
        const firstPrice = prices[0];
        const lastPrice = prices[prices.length - 1];
        
        return {
            total_return: ((lastPrice - firstPrice) / firstPrice) * 100,
            start_price: firstPrice,
            end_price: lastPrice,
            data_points: prices.length
        };
    }
}

// Usage example
const api = new MSEHistoricalAPI("your_api_key_here");

// Get single stock data
api.getHistoricalData("AIRTEL", "6months")
    .then(data => {
        if (data) {
            console.log(`AIRTEL: ${data.data_points} data points`);
            console.log(`Source: ${data.source}`);
            console.log(`Latest price: ${data.stock_prices[data.stock_prices.length - 1].price}`);
        }
    });

// Portfolio analysis
const portfolio = {
    "AIRTEL": 30,  // 30% allocation
    "NBM": 25,     // 25% allocation
    "TNM": 20,     // 20% allocation
    "STANDARD": 25 // 25% allocation
};

api.getPortfolioData(portfolio)
    .then(portfolioData => {
        for (const [symbol, data] of Object.entries(portfolioData)) {
            const returns = api.calculateReturns(data);
            console.log(`${symbol} (${data.allocation}%): ${returns.total_return.toFixed(2)}% return`);
        }
    });
```

### PHP - Web Application Integration

```php
<?php
class MSEHistoricalAPI {
    private $apiKey;
    private $baseUrl;
    
    public function __construct($apiKey, $baseUrl = "https://your-domain.com") {
        $this->apiKey = $apiKey;
        $this->baseUrl = $baseUrl;
    }
    
    public function getHistoricalData($symbol, $timeRange = "1month", $options = []) {
        $useCache = $options['cache'] ?? true;
        $forceRefresh = $options['refresh'] ?? false;
        
        $url = $this->baseUrl . "/api/historical/" . strtoupper($symbol) . "/";
        $params = http_build_query([
            'range' => $timeRange,
            'cache' => $useCache ? 'true' : 'false',
            'refresh' => $forceRefresh ? 'true' : 'false'
        ]);
        
        $context = stream_context_create([
            'http' => [
                'method' => 'GET',
                'header' => "X-API-Key: " . $this->apiKey
            ]
        ]);
        
        $response = file_get_contents($url . "?" . $params, false, $context);
        
        if ($response === false) {
            return null;
        }
        
        return json_decode($response, true);
    }
    
    public function getTopPerformers($symbols, $timeRange = "1month") {
        $results = [];
        
        foreach ($symbols as $symbol) {
            $data = $this->getHistoricalData($symbol, $timeRange);
            if ($data && !empty($data['stock_prices'])) {
                $prices = array_column($data['stock_prices'], 'price');
                $firstPrice = $prices[0];
                $lastPrice = end($prices);
                $return = (($lastPrice - $firstPrice) / $firstPrice) * 100;
                
                $results[$symbol] = [
                    'return' => $return,
                    'start_price' => $firstPrice,
                    'end_price' => $lastPrice,
                    'data_points' => count($prices)
                ];
            }
        }
        
        // Sort by return descending
        uasort($results, function($a, $b) {
            return $b['return'] <=> $a['return'];
        });
        
        return $results;
    }
}

// Usage example
$api = new MSEHistoricalAPI("your_api_key_here");

// Get data for major stocks
$majorStocks = ["AIRTEL", "TNM", "NBM", "STANDARD"];
$performers = $api->getTopPerformers($majorStocks, "3months");

echo "<h2>Top Performers (3 months)</h2>";
foreach ($performers as $symbol => $data) {
    echo "<p><strong>$symbol</strong>: " . number_format($data['return'], 2) . "% return</p>";
}
?>
```

## 🔄 Caching Strategy

### How Caching Works

1. **First Request**: Data is fetched from MSE website (~2-3 seconds)
2. **Subsequent Requests**: Data served from cache (~30-50ms)
3. **Cache Expiration**: 
   - Recent data (1-3 months): 6 hours
   - Older data (6+ months): 24 hours
4. **Daily Refresh**: Cache automatically refreshed at market close

### Cache Control

```python
# Use cached data (default, fastest)
data = api.get_historical_data("AIRTEL", "1month")

# Bypass cache for real-time data
fresh_data = api.get_historical_data("AIRTEL", "1month", use_cache=False)

# Force refresh (updates cache)
refreshed_data = api.get_historical_data("AIRTEL", "1month", force_refresh=True)
```

## ⚡ Performance Tips

### 1. Batch Requests Efficiently
```python
# Good: Request multiple time ranges for same stock
symbol = "AIRTEL"
short_term = api.get_historical_data(symbol, "1month")
long_term = api.get_historical_data(symbol, "1year")

# Better: Use caching for repeated requests
# First call fetches and caches
data1 = api.get_historical_data("TNM", "6months")
# Second call uses cache (much faster)
data2 = api.get_historical_data("TNM", "6months")
```

### 2. Choose Appropriate Time Ranges
```python
# For charts: Use appropriate granularity
daily_chart = api.get_historical_data("NBM", "1month")    # ~22 points
weekly_chart = api.get_historical_data("NBM", "6months")  # ~120 points
monthly_chart = api.get_historical_data("NBM", "2years") # ~480 points
```

### 3. Handle Errors Gracefully
```python
def safe_get_data(api, symbol, time_range):
    try:
        data = api.get_historical_data(symbol, time_range)
        if data and data.get('stock_prices'):
            return data
        else:
            print(f"No data available for {symbol}")
            return None
    except Exception as e:
        print(f"Error fetching {symbol}: {e}")
        return None
```

## 🚨 Error Handling

### Common Error Responses

```json
// Invalid symbol
{
  "error": "Could not retrieve historical data for XYZ",
  "message": "Data may not be available for this symbol or time range"
}

// Invalid time range
{
  "error": "Invalid time range specified",
  "valid_ranges": ["1month", "3months", "6months", "1year", "2years", "5years"]
}

// Rate limit exceeded
{
  "error": "Quota exceeded",
  "message": "Monthly API limit reached. Upgrade your plan or wait for reset."
}

// Invalid API key
{
  "error": "API key required",
  "message": "Please provide an API key in the X-API-Key header"
}
```

### Error Handling Best Practices

```python
import requests
from requests.exceptions import RequestException, HTTPError, Timeout

def robust_api_call(api_key, symbol, time_range="1month", max_retries=3):
    headers = {'X-API-Key': api_key}
    url = f"https://your-domain.com/api/historical/{symbol}/"
    params = {'range': time_range}
    
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=headers, params=params, timeout=30)
            response.raise_for_status()  # Raises HTTPError for bad status codes
            
            data = response.json()
            
            # Validate response structure
            if not data.get('stock_prices'):
                raise ValueError("Invalid response structure: missing stock_prices")
                
            return data
            
        except HTTPError as e:
            if response.status_code == 429:  # Rate limit
                print(f"Rate limit exceeded. Waiting before retry...")
                time.sleep(60)  # Wait 1 minute
            elif response.status_code in [401, 403]:  # Auth errors
                print(f"Authentication error: {e}")
                break  # Don't retry auth errors
            else:
                print(f"HTTP error on attempt {attempt + 1}: {e}")
                
        except Timeout:
            print(f"Request timeout on attempt {attempt + 1}")
            
        except RequestException as e:
            print(f"Request failed on attempt {attempt + 1}: {e}")
            
        except ValueError as e:
            print(f"Data validation error: {e}")
            break  # Don't retry validation errors
            
        if attempt < max_retries - 1:
            time.sleep(2 ** attempt)  # Exponential backoff
    
    return None
```

## 📊 Data Analysis Examples

### 1. Calculate Moving Averages

```python
def calculate_moving_average(price_data, window=5):
    prices = [float(p['price']) for p in price_data['stock_prices']]
    if len(prices) < window:
        return []
    
    moving_averages = []
    for i in range(len(prices) - window + 1):
        avg = sum(prices[i:i + window]) / window
        moving_averages.append({
            'date': price_data['stock_prices'][i + window - 1]['date'],
            'price': prices[i + window - 1],
            'ma': round(avg, 2)
        })
    
    return moving_averages

# Usage
airtel_data = api.get_historical_data("AIRTEL", "3months")
ma_data = calculate_moving_average(airtel_data, window=5)
print(f"5-day moving average for AIRTEL: {ma_data[-1]['ma']}")
```

### 2. Compare Stock Performance

```python
def compare_stocks(api, symbols, time_range="6months"):
    results = {}
    
    for symbol in symbols:
        data = api.get_historical_data(symbol, time_range)
        if data and data['stock_prices']:
            prices = [p['price'] for p in data['stock_prices']]
            start_price = prices[0]
            end_price = prices[-1]
            
            results[symbol] = {
                'start_price': start_price,
                'end_price': end_price,
                'total_return': ((end_price - start_price) / start_price) * 100,
                'volatility': calculate_volatility(prices)
            }
    
    return results

def calculate_volatility(prices):
    import statistics
    if len(prices) < 2:
        return 0
    
    returns = []
    for i in range(1, len(prices)):
        daily_return = (prices[i] - prices[i-1]) / prices[i-1]
        returns.append(daily_return)
    
    return statistics.stdev(returns) * 100  # Convert to percentage

# Compare telecom stocks
telecom_comparison = compare_stocks(api, ["AIRTEL", "TNM"], "1year")
for symbol, metrics in telecom_comparison.items():
    print(f"{symbol}: {metrics['total_return']:.2f}% return, {metrics['volatility']:.2f}% volatility")
```

### 3. Portfolio Analysis

```python
def analyze_portfolio(api, portfolio_weights, time_range="1year"):
    """
    Analyze a portfolio of stocks
    portfolio_weights: dict like {"AIRTEL": 0.3, "TNM": 0.2, "NBM": 0.5}
    """
    portfolio_data = {}
    
    # Get data for all stocks
    for symbol, weight in portfolio_weights.items():
        data = api.get_historical_data(symbol, time_range)
        if data:
            portfolio_data[symbol] = {
                'data': data,
                'weight': weight
            }
    
    # Calculate portfolio metrics
    all_dates = set()
    for symbol_data in portfolio_data.values():
        dates = [p['date'] for p in symbol_data['data']['stock_prices']]
        all_dates.update(dates)
    
    all_dates = sorted(list(all_dates))
    portfolio_values = []
    
    for date in all_dates:
        portfolio_value = 0
        valid_data = True
        
        for symbol, info in portfolio_data.items():
            price_on_date = None
            for price_point in info['data']['stock_prices']:
                if price_point['date'] == date:
                    price_on_date = price_point['price']
                    break
            
            if price_on_date is None:
                valid_data = False
                break
            
            portfolio_value += price_on_date * info['weight']
        
        if valid_data:
            portfolio_values.append({
                'date': date,
                'value': portfolio_value
            })
    
    # Calculate returns
    if len(portfolio_values) >= 2:
        start_value = portfolio_values[0]['value']
        end_value = portfolio_values[-1]['value']
        total_return = ((end_value - start_value) / start_value) * 100
        
        return {
            'portfolio_values': portfolio_values,
            'total_return': total_return,
            'start_value': start_value,
            'end_value': end_value
        }
    
    return None

# Example portfolio analysis
my_portfolio = {
    "AIRTEL": 0.25,
    "TNM": 0.15,
    "NBM": 0.30,
    "STANDARD": 0.30
}

portfolio_analysis = analyze_portfolio(api, my_portfolio, "6months")
if portfolio_analysis:
    print(f"Portfolio return: {portfolio_analysis['total_return']:.2f}%")
```

## 🔗 Integration Examples

### Django Web Application

```python
# views.py
from django.http import JsonResponse
from django.views import View
import requests

class StockChartView(View):
    def get(self, request, symbol):
        api_key = settings.MSE_API_KEY
        time_range = request.GET.get('range', '1month')
        
        headers = {'X-API-Key': api_key}
        url = f"https://your-domain.com/api/historical/{symbol}/"
        params = {'range': time_range}
        
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            
            # Format for Chart.js
            chart_data = {
                'labels': [p['date'] for p in data['stock_prices']],
                'datasets': [{
                    'label': f"{symbol} Price",
                    'data': [p['price'] for p in data['stock_prices']],
                    'borderColor': 'rgb(75, 192, 192)',
                    'backgroundColor': 'rgba(75, 192, 192, 0.1)',
                }]
            }
            
            return JsonResponse(chart_data)
            
        except requests.RequestException as e:
            return JsonResponse({'error': str(e)}, status=500)
```

### React Component

```jsx
import React, { useState, useEffect } from 'react';
import { Line } from 'react-chartjs-2';

const StockChart = ({ symbol, apiKey }) => {
    const [chartData, setChartData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [timeRange, setTimeRange] = useState('1month');

    useEffect(() => {
        const fetchData = async () => {
            setLoading(true);
            try {
                const response = await fetch(
                    `https://your-domain.com/api/historical/${symbol}/?range=${timeRange}`,
                    {
                        headers: {
                            'X-API-Key': apiKey
                        }
                    }
                );
                const data = await response.json();
                
                setChartData({
                    labels: data.stock_prices.map(p => p.date),
                    datasets: [{
                        label: `${symbol} Price`,
                        data: data.stock_prices.map(p => p.price),
                        borderColor: 'rgb(75, 192, 192)',
                        backgroundColor: 'rgba(75, 192, 192, 0.1)',
                    }]
                });
            } catch (error) {
                console.error('Error fetching data:', error);
            }
            setLoading(false);
        };

        fetchData();
    }, [symbol, timeRange, apiKey]);

    return (
        <div>
            <div>
                <select value={timeRange} onChange={(e) => setTimeRange(e.target.value)}>
                    <option value="1month">1 Month</option>
                    <option value="3months">3 Months</option>
                    <option value="6months">6 Months</option>
                    <option value="1year">1 Year</option>
                </select>
            </div>
            {loading ? (
                <div>Loading...</div>
            ) : chartData ? (
                <Line data={chartData} />
            ) : (
                <div>Error loading data</div>
            )}
        </div>
    );
};

export default StockChart;
```

## 📱 Mobile App Integration

### Flutter/Dart Example

```dart
import 'dart:convert';
import 'package:http/http.dart' as http;

class MSEHistoricalAPI {
  final String apiKey;
  final String baseUrl;

  MSEHistoricalAPI(this.apiKey, {this.baseUrl = "https://your-domain.com"});

  Future<Map<String, dynamic>?> getHistoricalData(
    String symbol, {
    String timeRange = "1month",
    bool useCache = true,
    bool forceRefresh = false,
  }) async {
    final uri = Uri.parse('$baseUrl/api/historical/${symbol.toUpperCase()}/')
        .replace(queryParameters: {
      'range': timeRange,
      'cache': useCache.toString(),
      'refresh': forceRefresh.toString(),
    });

    try {
      final response = await http.get(
        uri,
        headers: {'X-API-Key': apiKey},
      );

      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        print('API request failed: ${response.statusCode}');
        return null;
      }
    } catch (e) {
      print('Error fetching data: $e');
      return null;
    }
  }
}

// Usage in Flutter widget
class StockPriceWidget extends StatefulWidget {
  final String symbol;
  final String apiKey;

  StockPriceWidget({required this.symbol, required this.apiKey});

  @override
  _StockPriceWidgetState createState() => _StockPriceWidgetState();
}

class _StockPriceWidgetState extends State<StockPriceWidget> {
  Map<String, dynamic>? stockData;
  bool isLoading = true;

  @override
  void initState() {
    super.initState();
    loadData();
  }

  Future<void> loadData() async {
    final api = MSEHistoricalAPI(widget.apiKey);
    final data = await api.getHistoricalData(widget.symbol);
    
    setState(() {
      stockData = data;
      isLoading = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    if (isLoading) {
      return CircularProgressIndicator();
    }

    if (stockData == null) {
      return Text('Error loading data');
    }

    final prices = stockData!['stock_prices'] as List;
    final latestPrice = prices.isNotEmpty ? prices.last['price'] : 0;

    return Column(
      children: [
        Text(
          widget.symbol,
          style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
        ),
        Text(
          'MWK ${latestPrice.toString()}',
          style: TextStyle(fontSize: 20),
        ),
        Text('${prices.length} data points'),
      ],
    );
  }
}
```

## 🎯 Best Practices

### 1. API Key Security
- Store API keys in environment variables
- Never commit API keys to version control
- Use different keys for development and production
- Rotate keys regularly

### 2. Efficient Data Usage
- Use caching for repeated requests
- Choose appropriate time ranges for your use case
- Batch requests when possible
- Handle errors gracefully

### 3. Performance Optimization
- Cache responses on your end for frequently accessed data
- Use appropriate time ranges (don't fetch 5 years of data for a daily chart)
- Implement proper error handling and retries
- Monitor your API usage

### 4. Data Validation
- Always validate API responses
- Check for required fields before processing
- Handle missing or null data gracefully
- Implement fallback mechanisms

## 📞 Support & Resources

- **API Documentation**: `/swagger/` endpoint
- **Dashboard**: Monitor usage and manage keys
- **Status Page**: Check API health and maintenance windows
- **Support**: Contact through your dashboard

---

**Happy coding! Your comprehensive MSE data integration starts here. 📈🚀**
