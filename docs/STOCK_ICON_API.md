# Stock Icon API Documentation

## Overview
The Stock Icon API provides public access to stock symbol images/icons without requiring authentication. This is useful for displaying company logos or icons in applications that consume the MSE API.

## Endpoints

### 1. List All Available Icons
**GET** `/api/stock-icons/`

Returns a list of all available stock symbol icons.

**Response:**
```json
{
  "total_icons": 16,
  "available_icons": [
    {
      "symbol": "AIRTEL",
      "filename": "AIRTEL.png",
      "format": "png",
      "size_bytes": 15432,
      "url": "/api/stock-icon/AIRTEL/"
    },
    {
      "symbol": "TNM",
      "filename": "TNM.jpeg",
      "format": "jpeg",
      "size_bytes": 23145,
      "url": "/api/stock-icon/TNM/"
    }
  ],
  "supported_formats": ["png", "jpeg", "jpg"],
  "usage": "GET /api/stock-icon/{symbol}/ to get individual icons"
}
```

### 2. Get Individual Stock Icon
**GET** `/api/stock-icon/{symbol}/`

Returns the image file for the specified stock symbol.

**Parameters:**
- `symbol` (string): Stock symbol (case insensitive, e.g., "TNM", "airtel", "FCB")

**Response:**
- **Success (200)**: Returns the image file with appropriate content type
  - Content-Type: `image/png` or `image/jpeg`
  - Cache-Control: `public, max-age=86400` (24 hours)
  - Access-Control-Allow-Origin: `*` (CORS enabled)

- **Not Found (404)**: If no image exists for the symbol

**Supported Formats:**
- PNG (.png)
- JPEG (.jpeg, .jpg)

## Usage Examples

### cURL
```bash
# List all icons
curl http://localhost:8000/api/stock-icons/

# Get specific icon
curl http://localhost:8000/api/stock-icon/TNM/ --output tnm_icon.png
```

### JavaScript/Web
```javascript
// List all icons
fetch('/api/stock-icons/')
  .then(response => response.json())
  .then(data => console.log(data.available_icons));

// Use icon in HTML
<img src="/api/stock-icon/TNM/" alt="TNM Logo" />
```

### Python
```python
import requests

# List all icons
response = requests.get('http://localhost:8000/api/stock-icons/')
icons = response.json()

# Download specific icon
response = requests.get('http://localhost:8000/api/stock-icon/TNM/')
with open('tnm_icon.png', 'wb') as f:
    f.write(response.content)
```

## Available Stock Symbols
Based on current images in the system:
- AIRTEL
- BHL
- FCB
- FDHB
- ICON
- ILLOVO
- MPICO
- NB
- NBS
- NICO
- NITL
- OMU
- PCL
- STANDARD
- SUNBIRD
- TNM

## Features

### Public Access
- ✅ No API key required
- ✅ No authentication needed
- ✅ CORS enabled for web applications

### Performance
- ✅ 24-hour browser caching
- ✅ Direct file serving
- ✅ Optimized for web usage

### Error Handling
- ✅ 404 for missing images
- ✅ Case-insensitive symbol matching
- ✅ Multiple format support

## Integration Tips

1. **Caching**: Images are cached for 24 hours by browsers
2. **Fallbacks**: Always provide fallback images for symbols without icons
3. **Size**: Icons are optimized but sizes vary; consider CSS sizing
4. **Format**: PNG files support transparency; JPEG files are smaller
5. **CORS**: Can be used directly from web applications

## Error Responses

### 404 Not Found
```json
{
  "detail": "Image not found for symbol INVALID"
}
```

### 500 Server Error
```json
{
  "error": "Error loading image for symbol TNM",
  "message": "File access error"
}
```
