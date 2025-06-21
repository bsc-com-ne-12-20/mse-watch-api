# MSE-DATA: Malawi Stock Exchange API

A Django REST API for retrieving and managing Malawi Stock Exchange (MSE) data, including real-time stock prices, historical data, and company information.

## Features

- **Real-time Stock Data**: Scrape and store current stock prices from the Malawi Stock Exchange
- **Company Information**: Comprehensive company data for listed stocks
- **Historical Price Data**: Access to historical stock price information with OHLC (Open, High, Low, Close) data
- **REST API**: Clean, documented API endpoints for accessing all data
- **Market Session Awareness**: Intelligent scraping based on market session status
- **Command-line Tools**: Management commands for data collection and maintenance

## Installation

### Prerequisites

- Python 3.8+
- Django 5.x
- pip

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/MSE-DATA.git
   cd MSE-DATA/mse-data
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install django djangorestframework drf-yasg requests
   ```

4. Run migrations:
   ```bash
   cd mse_api
   python manage.py migrate
   ```

5. Set MSE cookies for authenticated requests:
   ```bash
   python manage.py set_mse_cookies "your_cookie_string"
   ```
   Note: You'll need to obtain cookies from a logged-in MSE session.

## Usage

### Starting the API Server

```bash
cd mse_api
python manage.py runserver
```

The API will be available at http://127.0.0.1:8000/

### Data Collection

Scrape current stock prices:
```bash
python manage.py scrape_stocks
```

Import company information:
```bash
python manage.py import_company_data
```

Fetch historical price data:
```bash
python manage.py fetch_historical_data --range 1month
```

Available ranges: `1month`, `3months`, `6months`, `1year`, `ytd`, `2years`, `3years`, `5years`, `all`

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `/api/prices/` | List all stock prices |
| `/api/latest/` | Get the latest price for each stock |
| `/api/by-datetime/` | Get stock prices at a specific date and time |
| `/api/companies/` | List all companies |
| `/api/company/<symbol>/` | Get details for a specific company |
| `/api/historical/<symbol>/` | **Get historical prices with smart caching** |

### 📈 Historical Data API (Featured)

Our newly rebuilt historical data endpoint provides:

- **📊 Complete MSE Coverage**: All 16 listed companies supported
- **⚡ Smart Caching**: 30-50ms response times for cached data
- **🔄 Real-time Scraping**: Fresh data from mse.co.mw when needed
- **📅 Multiple Time Ranges**: 1 month to 5 years of historical data
- **🛡️ Reliable**: Automatic cache refresh and error handling

**Quick Example:**
```bash
# Get 3 months of AIRTEL historical data
curl -H "X-API-Key: your_api_key" \
     "https://your-domain.com/api/historical/AIRTEL/?range=3months"
```

**📖 Complete Documentation**: See [`docs/HISTORICAL_DATA_GUIDE.md`](docs/HISTORICAL_DATA_GUIDE.md) for detailed examples, code samples, and integration guides.

### Query Parameters

#### `/stocks/by-datetime/`
- `date`: Date in YYYY-MM-DD format (required)
- `time`: Time in HH:MM:SS format (optional)
- `symbol`: Stock symbol (optional)
- `latest_only`: If 'true', return only the latest price for each symbol (default: true)

#### `/stocks/historical/<symbol>/`
- `start_date`: Start date in YYYY-MM-DD format (optional)
- `end_date`: End date in YYYY-MM-DD format (optional)
- `period`: Time range (1month, 3months, 6months, 1year, ytd, 2years, 3years, 5years) (optional)

## Data Models

### Company
Stores detailed information about listed companies including:
- Basic details (symbol, name, description)
- Contact information (website, address, phone, email)
- MSE-specific data (code, management info)
- Financial information (listing date, shares in issue)

### StockPrice
Stores current and recent stock prices:
- Symbol, price, change, direction
- Date and time information
- Market status updates

### HistoricalPrice
Stores historical OHLC (Open, High, Low, Close) data:
- Symbol and date
- Price data (open, high, low, close)
- Volume and turnover information

## Development

### Project Structure

```
mse-data/
├── mse_api/
│   ├── config/           # Django project settings
│   ├── stocks/           # Main app
│   │   ├── management/   # Custom management commands
│   │   │   └── commands/ # Implementation of scrapers and data collectors
│   │   ├── migrations/   # Database migrations
│   │   ├── services/     # Business logic and external service interactions
│   │   ├── models.py     # Data models
│   │   ├── serializers.py # API serializers
│   │   ├── urls.py       # API endpoint routing
│   │   └── views.py      # API view implementations
│   ├── data/             # CSV data files from scraping
│   └── manage.py         # Django management script
```

### Adding New Features

1. Define models in `stocks/models.py`
2. Create serializers in `stocks/serializers.py`
3. Implement views in `stocks/views.py`
4. Add URL routes in `stocks/urls.py`

## License

[MIT License](LICENSE)

## Acknowledgements

- [Django REST framework](https://www.django-rest-framework.org/)
- [Malawi Stock Exchange](https://mse.today/)
