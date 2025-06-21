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
| `/api/historical/{symbol}/` | Historical prices | Price history for a company |

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
