# 🚀 Quick Reference: Intraday API

## One-Line Usage

```bash
curl -H "X-API-Key: YOUR_KEY" "http://localhost:8000/api/historical/AIRTEL/?range=1day"
```

## Response Summary

```json
{
  "symbol": "AIRTEL",
  "date": "2025-06-23", 
  "open": 127.56,
  "high": 127.56,
  "low": 127.48,
  "close": 127.48,
  "data_points": 49,
  "market_sessions": ["Pre-Open", "Open"],
  "intraday_prices": [/* 49 price entries */]
}
```

## Parameters

- **URL**: `/api/historical/{SYMBOL}/`
- **Query**: `?range=1day`
- **Header**: `X-API-Key: your_key`

## Supported Symbols
`AIRTEL`, `TNM`, `NBM`, `STANDARD`, `BHL`, `FDHB`, `FMBCH`, `ICON`, `ILLOVO`, `MPICO`, `NBS`, `NICO`, `NITL`, `OMU`, `PCL`, `SUNBIRD`

---
📖 **[Full Documentation](INTRADAY_API_GUIDE.md)** | 🏠 **[Main API Docs](API_GUIDE.md)**
