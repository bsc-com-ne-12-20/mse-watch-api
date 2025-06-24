# Intraday Data API Documentation

## 1Day Intraday Endpoint

The 1day endpoint provides real-time intraday price data for stocks, showing all price movements throughout a trading day with market session identification.

---

## 📡 **Endpoint**

```
GET /api/historical/{symbol}/
```

### **URL Parameters**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `symbol` | string | ✅ Yes | Stock symbol (e.g., AIRTEL, NBM, NICO) |

### **Query Parameters**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `range` | string | ✅ Yes | - | Must be `"1day"` for intraday data |
| `cache` | boolean | ❌ No | `true` | Whether to use cached data |
| `refresh` | boolean | ❌ No | `false` | Force refresh data (ignores cache) |

---

## 🔑 **Authentication**

Required header:
```
X-API-Key: your_api_key_here
```

---

## 📋 **Example Request**

```bash
curl -X GET "http://localhost:8000/api/historical/AIRTEL/?range=1day" \
  -H "X-API-Key: mse_5PFAyspVWQnz33boHidjCIiU2y6aNoEmzZteXzRV" \
  -H "Content-Type: application/json"
```

---

## 📊 **Response Format**

### **Success Response (200 OK)**

```json
{
  "symbol": "AIRTEL",
  "date": "2025-06-23",
  "open": 127.56,
  "high": 127.56,
  "low": 127.48,
  "close": 127.48,
  "data_points": 49,
  "market_sessions": [
    "Pre-Open",
    "Open"
  ],
  "intraday_prices": [
    {
      "time": "09:01:01",
      "price": 127.56,
      "change": -0.01,
      "direction": "down",
      "market_status": "Pre-Open"
    },
    {
      "time": "09:30:21",
      "price": 127.56,
      "change": 0.0,
      "direction": "no change",
      "market_status": "Open"
    },
    {
      "time": "11:26:18",
      "price": 127.48,
      "change": -0.08,
      "direction": "down",
      "market_status": "Open"
    }
  ]
}
```

### **Response Fields**

| Field | Type | Description |
|-------|------|-------------|
| `symbol` | string | Stock symbol in uppercase |
| `date` | string | Trading date (ISO format: YYYY-MM-DD) |
| `open` | number | Opening price for the day |
| `high` | number | Highest price during the day |
| `low` | number | Lowest price during the day |
| `close` | number | Closing price for the day |
| `data_points` | integer | Number of intraday price points |
| `market_sessions` | array | List of market sessions present in the data |
| `intraday_prices` | array | Array of individual price entries |

### **Intraday Price Entry Fields**

| Field | Type | Description |
|-------|------|-------------|
| `time` | string | Time of price update (HH:MM:SS format) |
| `price` | number | Stock price at that time |
| `change` | number | Price change from previous day's close |
| `direction` | string | Price movement: `"up"`, `"down"`, or `"no change"` |
| `market_status` | string | Market session: `"Pre-Open"`, `"Open"`, `"Close"`, `"Post-Close"` |

---

## 🕐 **Market Sessions**

| Session | Time Range | Description |
|---------|------------|-------------|
| **Pre-Open** | 09:00 - 09:30 | Pre-market trading session |
| **Open** | 09:30 - 14:30 | Main trading session |
| **Close** | 14:30 - 15:00 | Closing auction session |
| **Post-Close** | 15:00 - 17:00 | Post-market session |
| **After-Hours** | Outside above | Non-trading hours |

---

## ⚠️ **Error Responses**

### **401 Unauthorized**
```json
{
  "error": "API key required",
  "message": "Please provide an API key in the X-API-Key header"
}
```

### **404 Not Found**
```json
{
  "error": "Could not retrieve historical data for INVALID",
  "message": "Data may not be available for this symbol or time range"
}
```

### **400 Bad Request**
```json
{
  "error": "Invalid time range",
  "message": "Valid ranges: 1day, 1month, 3months, 6months, 1year, 2years, 5years"
}
```

---

## 🎯 **Data Behavior**

### **Current Day vs Previous Day**
- **Current Trading Day**: Returns real-time intraday data if available
- **Non-Trading Day**: Automatically falls back to the most recent trading day
- **Weekends/Holidays**: Returns data from the last trading day

### **Caching Strategy**
- **Cache Duration**: 1 hour for intraday data
- **Cache Key**: Includes symbol, date, and current hour
- **Refresh**: Set `refresh=true` to bypass cache and get fresh data

### **Data Freshness**
- Updates automatically as your scheduler collects new price data
- Typical update frequency: Every 5-15 minutes during trading hours
- Real-time during market hours, static after market close

---

## 📈 **Use Cases**

1. **Real-time Trading Dashboards**: Display live price movements
2. **Market Analysis**: Analyze intraday price patterns and volatility
3. **Trading Algorithms**: Feed intraday data for automated trading decisions
4. **Financial Charts**: Create candlestick or line charts with intraday data
5. **Market Research**: Study market behavior during different sessions

---

## 💡 **Example Use Cases**

### **Get Latest Intraday Data**
```javascript
// Always get the freshest data
fetch('/api/historical/AIRTEL/?range=1day&refresh=true')
```

### **Build Real-time Chart**
```javascript
// Use cached data for better performance
fetch('/api/historical/NBM/?range=1day&cache=true')
  .then(response => response.json())
  .then(data => {
    // data.intraday_prices contains all price points
    // Use for charts, analysis, etc.
  });
```

### **Monitor Market Sessions**
```javascript
// Check which market sessions are active
const data = await fetch('/api/historical/NICO/?range=1day');
console.log('Active sessions:', data.market_sessions);
```

---

## ⚡ **Performance Notes**

- **Response Time**: ~200-500ms (depending on cache status)
- **Data Size**: Typically 20-100 price points per trading day
- **Rate Limits**: Subject to your API key's rate limiting
- **Best Practice**: Use caching for frequent requests, refresh for critical updates
