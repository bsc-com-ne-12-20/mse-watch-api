from django.db import models

class StockPrice(models.Model):
    symbol = models.CharField(max_length=20)
    price = models.FloatField()
    change = models.FloatField()
    direction = models.CharField(max_length=10)
    date = models.DateField()
    time = models.TimeField()
    market_status = models.CharField(max_length=20)
    market_update_time = models.CharField(max_length=30)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-date', '-time', 'symbol']
        
    def __str__(self):
        return f"{self.symbol} ({self.date}): {self.price}"