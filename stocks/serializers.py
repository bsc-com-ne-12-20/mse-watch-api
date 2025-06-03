from rest_framework import serializers
from .models import StockPrice

class StockPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockPrice
        fields = ['id', 'symbol', 'price', 'change', 'direction', 'date', 
                  'time', 'market_status', 'market_update_time']