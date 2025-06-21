from rest_framework import viewsets, filters, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.db.models import Max
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, Http404
from django.conf import settings
from django.core.cache import cache
import os
from .models import StockPrice, Company, HistoricalPrice, Subscriber
from .serializers import StockPriceSerializer, CompanySerializer, SubscriberSerializer
from datetime import datetime, timedelta, date
import logging

from .services.historical_service import MSEHistoricalService

logger = logging.getLogger(__name__)

@api_view(['GET'])
def stock_icons_list(request):
    """
    List all available stock icons - Public endpoint (no authentication required)
    
    Returns a list of all available stock symbol icons with their URLs.
    
    Response:
    - JSON object with available icons and their metadata
    """
    try:
        # Get images directory
        images_dir = os.path.join(settings.BASE_DIR, 'staticfiles', 'images')
        
        if not os.path.exists(images_dir):
            return Response({
                'error': 'Images directory not found',
                'available_icons': []
            }, status=404)
        
        # Get all image files
        available_icons = []
        supported_extensions = ['.png', '.jpeg', '.jpg']
        
        for filename in os.listdir(images_dir):
            file_path = os.path.join(images_dir, filename)
            if os.path.isfile(file_path):
                name, ext = os.path.splitext(filename)
                if ext.lower() in supported_extensions:
                    # Get file size
                    file_size = os.path.getsize(file_path)
                    
                    icon_info = {
                        'symbol': name.upper(),
                        'filename': filename,
                        'format': ext.lower().replace('.', ''),
                        'size_bytes': file_size,
                        'url': f"/api/stock-icon/{name.upper()}/"
                    }
                    available_icons.append(icon_info)
        
        # Sort by symbol
        available_icons.sort(key=lambda x: x['symbol'])
        
        return Response({
            'total_icons': len(available_icons),
            'available_icons': available_icons,
            'supported_formats': ['png', 'jpeg', 'jpg'],
            'usage': 'GET /api/stock-icon/{symbol}/ to get individual icons'
        })
        
    except Exception as e:
        logger.error(f"Error listing stock icons: {str(e)}")
        return Response({
            'error': 'Error listing available icons',
            'message': str(e)
        }, status=500)

@api_view(['GET'])
def stock_icon(request, symbol):
    """
    Get stock symbol icon/image - Public endpoint (no authentication required)
    
    Returns the image file for the given stock symbol.
    Supports PNG, JPEG, and JPG formats.
    
    Parameters:
    - symbol: Stock symbol (e.g., TNM, AIRTEL, etc.)
    
    Response:
    - Image file with appropriate content type
    - 404 if image not found
    """
    symbol = symbol.upper()
    
    # Define possible image extensions
    extensions = ['.png', '.jpeg', '.jpg']
    
    # Look for the image file in staticfiles/images
    images_dir = os.path.join(settings.BASE_DIR, 'staticfiles', 'images')
    
    for ext in extensions:
        image_path = os.path.join(images_dir, f"{symbol}{ext}")
        if os.path.exists(image_path):
            try:
                # Determine content type based on extension
                content_type = 'image/png' if ext == '.png' else 'image/jpeg'
                
                # Read and return the image
                with open(image_path, 'rb') as f:
                    image_data = f.read()
                
                response = HttpResponse(image_data, content_type=content_type)
                response['Cache-Control'] = 'public, max-age=86400'  # Cache for 24 hours
                response['Access-Control-Allow-Origin'] = '*'  # Allow CORS for public endpoint
                return response
                
            except Exception as e:
                logger.error(f"Error serving image for {symbol}: {str(e)}")
                raise Http404(f"Error loading image for symbol {symbol}")
    
    # If no image found, return 404
    raise Http404(f"Image not found for symbol {symbol}")

class StockPriceViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows stock prices to be viewed.
    """
    queryset = StockPrice.objects.all()
    serializer_class = StockPriceSerializer
    permission_classes = [AllowAny]  # Use custom middleware for authentication
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['symbol']
    ordering_fields = ['date', 'time', 'price', 'change']

@api_view(['GET'])
def latest_prices(request):
    """
    Get the latest price for each stock symbol (limited to 16 symbols)
    """
    # Get the latest date
    latest_date = StockPrice.objects.aggregate(Max('date'))['date__max']
    
    if not latest_date:
        return Response([])
    
    # Get unique symbols from the latest date, limited to 16
    symbols = list(StockPrice.objects.filter(date=latest_date).values_list('symbol', flat=True).distinct()[:16])
    
    # For each symbol, get the latest record on that date
    latest_prices = []
    for symbol in symbols:
        latest = StockPrice.objects.filter(
            symbol=symbol, 
            date=latest_date
        ).order_by('-time').first()
        
        if latest:
            latest_prices.append(latest)
    
    # Sort by symbol for consistent ordering and ensure we don't exceed 16
    latest_prices.sort(key=lambda x: x.symbol)
    latest_prices = latest_prices[:16]  # Extra safety to ensure max 16 records
    
    serializer = StockPriceSerializer(latest_prices, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def prices_by_datetime(request):
    """
    Get stock prices at a specific date and time
    
    Query parameters:
    - date: Date in YYYY-MM-DD format
    - time: Time in HH:MM:SS format (optional)
    - symbol: Stock symbol (optional)
    - latest_only: If 'true', return only the latest price for each symbol (default: true)
    """
    date_str = request.query_params.get('date')
    time_str = request.query_params.get('time')
    symbol = request.query_params.get('symbol')
    # By default, return only the latest price for each symbol
    latest_only = request.query_params.get('latest_only', 'true').lower() == 'true'
    
    if not date_str:
        return Response(
            {"error": "Date parameter is required (format: YYYY-MM-DD)"}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Validate date format
        query_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        
        # Start with filtering by date
        queryset = StockPrice.objects.filter(date=query_date)
        
        # Filter by symbol if provided
        if symbol:
            queryset = queryset.filter(symbol=symbol)
        
        # Get distinct symbols for processing
        symbols = queryset.values_list('symbol', flat=True).distinct()
        
        # Initialize empty result list
        result = []
        
        # If time is provided, find the closest time for each symbol
        if time_str:
            try:
                query_time = datetime.strptime(time_str, "%H:%M:%S").time()
                
                # Process each symbol individually
                for sym in symbols:
                    # For each symbol, get prices ordered by time
                    symbol_prices = queryset.filter(symbol=sym).order_by('time')
                    
                    # Try to find price before or at the requested time
                    before_prices = symbol_prices.filter(time__lte=query_time).order_by('-time')
                    if before_prices.exists():
                        result.append(before_prices.first())
                    else:
                        # If no earlier price, get the earliest available
                        earliest = symbol_prices.first()
                        if earliest:
                            result.append(earliest)
                
            except ValueError:
                return Response(
                    {"error": "Invalid time format. Use HH:MM:SS"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        # If no time specified or if latest_only is true, get the latest price for each symbol
        elif latest_only or not time_str:
            # Process each symbol individually
            for sym in symbols:
                # For each symbol, get the latest price by time
                latest_price = queryset.filter(symbol=sym).order_by('-time').first()
                if latest_price:
                    result.append(latest_price)
        # If latest_only is false and no time specified, return all records (filtered by symbol if provided)
        else:
            # Convert queryset to list for consistency
            result = list(queryset)
        
        # Ensure we have no duplicates by converting to a dict with symbol as key
        # This is a safeguard against any logic issues that might produce duplicates
        unique_results = {}
        for item in result:
            if item.symbol not in unique_results or unique_results[item.symbol].time < item.time:
                unique_results[item.symbol] = item
        
        # Convert back to a list and sort by symbol
        final_result = sorted(unique_results.values(), key=lambda x: x.symbol)
        
        serializer = StockPriceSerializer(final_result, many=True)
        return Response(serializer.data)
    
    except ValueError:
        return Response(
            {"error": "Invalid date format. Use YYYY-MM-DD"}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return Response(
            {"error": str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

class CompanyViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows company information to be viewed.
    """
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [AllowAny]  # Use custom middleware for authentication
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['symbol', 'name', 'sector', 'industry']
    ordering_fields = ['symbol', 'name', 'sector', 'listed_date']

@api_view(['GET'])
def company_detail(request, symbol):
    """
    Get detailed information about a specific company including latest stock data
    """
    try:
        company = Company.objects.get(symbol=symbol.upper())
    except Company.DoesNotExist:
        return Response(
            {"error": f"Company with symbol '{symbol}' not found"}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Get the latest stock price
    latest_price = StockPrice.objects.filter(symbol=symbol.upper()).order_by('-date', '-time').first()
    
    # Serialize the company data
    company_data = CompanySerializer(company).data
    
    # Add market data if available
    if latest_price:
        market_data = {
            'current_price': latest_price.price,
            'price_change': latest_price.change,
            'percent_change': (latest_price.change / (latest_price.price - latest_price.change) * 100) if latest_price.price != latest_price.change else 0,
            'market_status': latest_price.market_status,
            'last_updated': f"{latest_price.date} {latest_price.time}",
            'market_cap': latest_price.price * company.shares_in_issue if company.shares_in_issue else None
        }
        company_data['market_data'] = market_data
    
    return Response(company_data)

@api_view(['GET'])
def historical_prices(request, symbol):
    """
    Get historical price data for a stock with smart caching
    
    Query parameters:
    - range: Time range (1month, 3months, 6months, 1year, 2years, 5years)
    - cache: Whether to use cached data (true/false, default: true)
    - refresh: Force refresh data from source (true/false, default: false)
    """
    # Process query parameters
    time_range = request.query_params.get('range', '1month')
    use_cache = request.query_params.get('cache', 'true').lower() == 'true'
    refresh = request.query_params.get('refresh', 'false').lower() == 'true'
    
    # Standardize symbol
    symbol = symbol.upper()
    
    logger.info(f"Fetching historical prices for {symbol} with range {time_range}, cache={use_cache}, refresh={refresh}")
    
    # Validate time range
    valid_ranges = ['1month', '3months', '6months', '1year', '2years', '5years']
    if time_range not in valid_ranges:
        time_range = '1month'
        logger.warning(f"Invalid time range. Using default '1month'.")
    
    # Generate cache key
    cache_key = f"historical_{symbol}_{time_range}_{date.today().isoformat()}"
    
    # Check cache first (unless refresh is forced)
    if use_cache and not refresh:
        cached_data = cache.get(cache_key)
        if cached_data:
            logger.info(f"Returning cached data for {symbol} {time_range}")
            cached_data['source'] = 'cache'
            return Response(cached_data)
        
        # Check database cache for older data
        db_data = get_cached_historical_data(symbol, time_range)
        if db_data.status_code == 200:
            logger.info(f"Returning database cached data for {symbol} {time_range}")
            return db_data
    
    # Fetch fresh data from MSE website
    service = MSEHistoricalService()
    historical_data = service.get_historical_data(symbol, time_range)
    
    if not historical_data:
        logger.warning(f"Could not retrieve historical data for {symbol} from service")
        return Response({
            "error": f"Could not retrieve historical data for {symbol}",
            "message": "Data may not be available for this symbol or time range"
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Save to database for future caching
    try:
        saved_count = service.save_to_database(symbol, historical_data)
        logger.info(f"Saved {saved_count} data points to database for {symbol}")
    except Exception as e:
        logger.error(f"Error saving to database: {e}")
    
    # Return the fresh data
    return Response(historical_data)

def get_cached_historical_data(symbol, time_range):
    """Get historical data from database cache"""
    # Map time ranges to date ranges
    today = datetime.now().date()
    
    if time_range == '1month':
        start_date = today - timedelta(days=31)
    elif time_range == '3months':
        start_date = today - timedelta(days=92)
    elif time_range == '6months':
        start_date = today - timedelta(days=183)
    elif time_range == '1year':
        start_date = today - timedelta(days=366)
    elif time_range == 'ytd':
        start_date = datetime(today.year, 1, 1).date()
    elif time_range == '2years':
        start_date = today - timedelta(days=731)
    elif time_range == '3years':
        start_date = today - timedelta(days=1096)
    elif time_range == '5years':
        start_date = today - timedelta(days=1827)
    else:
        start_date = today - timedelta(days=31)
    
    # Get historical prices from database
    prices = (
        HistoricalPrice.objects
        .filter(symbol=symbol, date__gte=start_date)
        .order_by('date')
    )
    
    if not prices.exists():
        logger.warning(f"No historical data found in cache for {symbol} in {time_range} range.")
        return Response({
            "error": f"No historical data found for {symbol} in {time_range} range"
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Get company info if available
    if prices.first().company:
        company = prices.first().company
        company_info = {
            'symbol': company.symbol,
            'name': company.name,
            'current_price': prices.last().price if prices.exists() else None,
            'listing_date': company.listed_date.isoformat() if company.listed_date else None,
            'listing_price': float(company.listing_price) if company.listing_price else None,
            'market_cap': None,  # Calculate if needed
            'shares_in_issue': company.shares_in_issue
        }
    else:
        company_info = {
            'symbol': symbol,
            'current_price': prices.last().price if prices.exists() else None,
        }
    
    # Format the response
    stock_prices = []
    for price in prices:
        stock_prices.append({
            'date': price.date.isoformat(),
            'open': float(price.open_price) if price.open_price else None,
            'high': float(price.high) if price.high else None,
            'low': float(price.low) if price.low else None,
            'close': float(price.close_price) if price.close_price else None,
            'volume': price.volume,
            'turnover': float(price.turnover) if price.turnover else None  # Make sure turnover is included
        })
    
    return Response({
        'company': company_info,
        'time_range': time_range,
        'stock_prices': stock_prices,
        'retrieved_at': datetime.now().isoformat(),
        'data_points': len(stock_prices),
        'source': 'cache'
    })

@api_view(['POST'])
def subscribe(request):
    """Subscribe to daily market reports"""
    serializer = SubscriberSerializer(data=request.data)
    if serializer.is_valid():
        # Check if email already exists but is inactive
        email = serializer.validated_data['email']
        existing = Subscriber.objects.filter(email=email).first()
        
        if existing:
            if not existing.is_active:
                existing.is_active = True
                existing.save()
                return Response({'message': 'Subscription reactivated successfully!'})
            return Response({'message': 'You are already subscribed!'})
        
        # Create new subscription
        serializer.save()
        return Response({'message': 'Subscribed successfully to daily market reports!'})
    return Response(serializer.errors, status=400)

@api_view(['GET'])
def unsubscribe(request, token):
    """Unsubscribe from daily market reports"""
    subscriber = get_object_or_404(Subscriber, unsubscribe_token=token)
    subscriber.is_active = False
    subscriber.save()
    return Response({'message': 'Unsubscribed successfully from daily market reports!'})

@api_view(['GET'])
def market_status(request):
    """
    Get current market status based on time and latest data
    """
    # Get current time
    current_time = datetime.now()
    current_weekday = current_time.weekday()
    current_hour = current_time.hour
    current_minute = current_time.minute
    current_time_value = current_hour * 60 + current_minute
    
    # Check if it's weekend
    if current_weekday in [5, 6]:  # Saturday or Sunday
        status = "Closed (Weekend)"
        session = "Weekend"
    else:
        # MSE market schedule (in minutes since midnight)
        if 9*60 <= current_time_value < 9*60+30:  # 9:00 - 9:30
            status = "Open"
            session = "Pre-Open"
        elif 9*60+30 <= current_time_value < 14*60+30:  # 9:30 - 14:30
            status = "Open"
            session = "Trading"
        elif 14*60+30 <= current_time_value < 15*60:  # 14:30 - 15:00
            status = "Open"
            session = "Close"
        elif 15*60 <= current_time_value <= 17*60:  # 15:00 - 17:00
            status = "Open"
            session = "Post-Close"
        else:
            status = "Closed"
            session = "After Hours"
    
    # Get the latest market data to see last update
    latest_price = StockPrice.objects.order_by('-date', '-time').first()
    last_update = None
    market_data_status = "Unknown"
    
    if latest_price:
        last_update = f"{latest_price.date} {latest_price.time}"
        market_data_status = latest_price.market_status
    
    return Response({
        'status': status,
        'session': session,
        'current_time': current_time.strftime('%Y-%m-%d %H:%M:%S'),
        'last_data_update': last_update,
        'market_data_status': market_data_status,
        'is_weekend': current_weekday in [5, 6],
        'trading_day': current_weekday < 5
    })