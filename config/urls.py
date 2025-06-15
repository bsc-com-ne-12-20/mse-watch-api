from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
   openapi.Info(
      title="MSE API",
      default_version='v1',
      description="Malawi Stock Exchange API",
      contact=openapi.Contact(email="contact@example.com"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('', TemplateView.as_view(template_name='landing.html'), name='landing'),
    path('admin/', admin.site.urls),
    path('api/', include('stocks.urls')),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

# Serve static files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)