from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'prices', views.StockPriceViewSet)
router.register(r'companies', views.CompanyViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('latest/', views.latest_prices, name='latest-prices'),
    path('market-status/', views.market_status, name='market-status'),
    path('background-status/', views.background_status, name='background-status'),
    path('by-datetime/', views.prices_by_datetime, name='prices-by-datetime'),
    path('company/<str:symbol>/', views.company_detail, name='company-detail'),  # Changed from 'companies/' to 'company/'
    path('historical/<str:symbol>/', views.historical_prices, name='historical-data'),
    path('stock-icons/', views.stock_icons_list, name='stock-icons-list'),  # Public endpoint to list all icons
    path('stock-icon/<str:symbol>/', views.stock_icon, name='stock-icon'),  # Public endpoint for stock icons
    path('subscribe/', views.subscribe, name='subscribe'),
    path('unsubscribe/<str:token>/', views.unsubscribe, name='unsubscribe'),
]