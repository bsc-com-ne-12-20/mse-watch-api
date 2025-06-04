from django.db import models

class Company(models.Model):
    """
    Model to store company information for stocks listed on MSE
    """
    symbol = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    sector = models.CharField(max_length=100, blank=True, null=True)
    industry = models.CharField(max_length=100, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    
    # Additional fields for MSE specific data
    code = models.CharField(max_length=20, blank=True, null=True)
    ceo = models.CharField(max_length=100, blank=True, null=True)
    cfo = models.CharField(max_length=100, blank=True, null=True)
    company_secretary = models.CharField(max_length=100, blank=True, null=True)
    transfer_secretary = models.CharField(max_length=200, blank=True, null=True)
    
    # Financial information
    listed_date = models.DateField(blank=True, null=True)
    listing_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    shares_in_issue = models.BigIntegerField(blank=True, null=True)
    
    # Metadata
    founded_year = models.PositiveIntegerField(blank=True, null=True)
    employees = models.PositiveIntegerField(blank=True, null=True)
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Companies"
        ordering = ['symbol']
    
    def __str__(self):
        return f"{self.symbol} - {self.name}"

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

class HistoricalPrice(models.Model):
    """Model for storing historical stock prices with OHLC data"""
    symbol = models.CharField(max_length=20, db_index=True)
    date = models.DateField(db_index=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Close price for consistency
    open_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    high = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    low = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    close_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    volume = models.BigIntegerField(null=True, blank=True)
    turnover = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)  # Make sure this field exists
    company = models.ForeignKey(
        'Company', 
        on_delete=models.CASCADE, 
        related_name='historical_prices',
        null=True, blank=True
    )
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('symbol', 'date')
        ordering = ['symbol', '-date']
        indexes = [
            models.Index(fields=['symbol', 'date']),
        ]
    
    def __str__(self):
        return f"{self.symbol} - {self.date} - {self.price}"