from django.contrib import admin
from .models import  StockPrice, Company, HistoricalPrice

#admin.site.register(Stock)
admin.site.register(StockPrice)
#admin.site.register(StockPriceHistory)
admin.site.register(Company)
admin.site.register(HistoricalPrice)


# Register your models here.
