from rest_framework import serializers
from .models import StockPrice, Company  # Import Company model

class StockPriceSerializer(serializers.ModelSerializer):
    percent_change = serializers.SerializerMethodField()
    
    class Meta:
        model = StockPrice
        fields = ['id', 'symbol', 'price', 'change', 'percent_change', 'direction', 'date', 
                  'time', 'market_status', 'market_update_time']
    
    def get_percent_change(self, obj):
        # Calculate percentage change
        # If price is 0, return 0 to avoid division by zero
        if obj.price == 0 or (obj.price - obj.change) == 0:
            return 0
        
        # Calculate percentage: (change / (price - change)) * 100
        previous_price = obj.price - obj.change
        percent_change = (obj.change / previous_price) * 100
        
        # Round to 4 decimal places to show small changes in high-value stocks
        return round(percent_change, 4)

# Make sure your CompanySerializer looks like this:

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = '__all__'