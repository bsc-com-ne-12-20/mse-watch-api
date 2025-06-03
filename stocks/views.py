from rest_framework import viewsets, filters, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Max
from .models import StockPrice
from .serializers import StockPriceSerializer
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
    """
    date_str = request.query_params.get('date')
    time_str = request.query_params.get('time')
    symbol = request.query_params.get('symbol')
    
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
        
        # If time is provided, find the closest time for each symbol
        if time_str:
            try:
                query_time = datetime.strptime(time_str, "%H:%M:%S").time()
                
                # Get distinct symbols
                symbols = queryset.values_list('symbol', flat=True).distinct()
                
                result = []
                for sym in symbols:
                    # For each symbol, get the entry with time closest to the requested time
                    symbol_prices = queryset.filter(symbol=sym).order_by('time')
                    
                    # Find closest time (earlier or later)
                    closest_price = None
                    
                    # Try to find price before the requested time
                    before_prices = symbol_prices.filter(time__lte=query_time).order_by('-time')
                    if before_prices.exists():
                        closest_price = before_prices.first()
                    else:
                        # If no earlier price, get the earliest available
                        closest_price = symbol_prices.first()
                    
                    if closest_price:
                        result.append(closest_price)
                
                queryset = result
            except ValueError:
                return Response(
                    {"error": "Invalid time format. Use HH:MM:SS"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Sort by symbol for consistent results
        if isinstance(queryset, list):
            queryset.sort(key=lambda x: x.symbol)
        else:
            queryset = queryset.order_by('symbol')
        
        serializer = StockPriceSerializer(queryset, many=True)
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