from rest_framework import viewsets, filters, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Max
from .models import StockPrice, Company
from .serializers import StockPriceSerializer, CompanySerializer
from datetime import datetime

class StockPriceViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows stock prices to be viewed.
    """
    queryset = StockPrice.objects.all()
    serializer_class = StockPriceSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['symbol']
    ordering_fields = ['date', 'time', 'price', 'change']

@api_view(['GET'])
def latest_prices(request):
    """
    Get the latest price for each stock symbol
    """
    # Get the latest date
    latest_date = StockPrice.objects.aggregate(Max('date'))['date__max']
    
    # For each symbol, get the latest record on that date
    latest_prices = []
    symbols = StockPrice.objects.filter(date=latest_date).values_list('symbol', flat=True).distinct()
    
    for symbol in symbols:
        latest = StockPrice.objects.filter(
            symbol=symbol, 
            date=latest_date
        ).order_by('-time').first()
        
        if latest:
            latest_prices.append(latest)
    
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