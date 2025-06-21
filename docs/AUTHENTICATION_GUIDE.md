# MSE API Authentication Guide

## Overview
The MSE API uses API key authentication for most endpoints, with a few public exceptions.

## Public Endpoints (No Authentication Required)

These endpoints can be accessed without an API key:

| Endpoint | Description |
|----------|-------------|
| `GET /api/stock-icons/` | List all available stock icons |
| `GET /api/stock-icon/{symbol}/` | Get specific stock icon image |
| `GET /api/docs/` | API documentation (Swagger) |
| `GET /api/schema/` | API schema |

## Protected Endpoints (API Key Required)

All other API endpoints require authentication:

| Endpoint | Description |
|----------|-------------|
| `GET /api/market-status/` | ⚠️ **NOW REQUIRES API KEY** |
| `GET /api/latest/` | Latest stock prices |
| `GET /api/companies/` | Company listings |
| `GET /api/company/{symbol}/` | Company details |
| `GET /api/historical/{symbol}/` | Historical price data |
| `GET /api/prices/` | Stock price data |
| `POST /api/subscribe/` | Subscribe to reports |

## Authentication Methods

### API Key Header
```http
GET /api/market-status/
X-API-Key: mse_your_api_key_here
```

### Authorization Header (Bearer)
```http
GET /api/market-status/
Authorization: Bearer mse_your_api_key_here
```

## Error Responses

### Missing API Key (401)
```json
{
  "error": "API key required",
  "message": "Please provide an API key in the X-API-Key header"
}
```

### Invalid API Key (401)
```json
{
  "error": "Invalid API key",
  "message": "The provided API key is invalid or inactive"
}
```

### Quota Exceeded (429)
```json
{
  "error": "Quota exceeded",
  "message": "Monthly limit of 100 requests exceeded"
}
```

## Testing Authentication

Use the provided test script to verify authentication:

```bash
python test_authentication.py
```

This will test both public and protected endpoints.

## Recent Changes

- **2025-06-21**: Market Status endpoint now requires API key authentication
- Stock icon endpoints remain public for easy integration
- All other data endpoints require authentication for quota tracking
