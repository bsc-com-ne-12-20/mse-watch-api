from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'prices', views.StockPriceViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('latest/', views.latest_prices, name='latest-prices'),
    path('by-datetime/', views.prices_by_datetime, name='prices-by-datetime'),
]