from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'prices', views.StockPriceViewSet)
router.register(r'companies', views.CompanyViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('latest/', views.latest_prices, name='latest-prices'),
    path('by-datetime/', views.prices_by_datetime, name='prices-by-datetime'),
    path('company/<str:symbol>/', views.company_detail, name='company-detail'),  # Changed from 'companies/' to 'company/'
    path('historical/<str:symbol>/', views.historical_prices, name='historical-prices'),
    path('subscribe/', views.subscribe, name='subscribe'),
    path('unsubscribe/<str:token>/', views.unsubscribe, name='unsubscribe'),
]