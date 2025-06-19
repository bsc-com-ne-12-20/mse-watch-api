# API Key Authentication Middleware
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from django.utils import timezone
from accounts.models import APIKey, APIUsage, UsageQuota
import json


class APIKeyMiddleware(MiddlewareMixin):
    """
    Middleware to authenticate API requests using API keys
    and track usage for quota enforcement
    """
    
    def process_request(self, request):
        # Only apply to API endpoints
        if not request.path.startswith('/api/'):
            return None        # Skip authentication for some endpoints (like market status which might be public)
        public_endpoints = [
            '/api/docs/', 
            '/api/schema/',
            '/api/stock-icons/',  # Public endpoint to list all available icons
            '/api/stock-icon/',  # Public endpoint for stock symbol icons
        ]
        if any(request.path.startswith(endpoint) for endpoint in public_endpoints):
            return None
            
        # Get API key from header
        api_key = request.META.get('HTTP_X_API_KEY') or request.META.get('HTTP_AUTHORIZATION')
        
        if api_key:
            # Remove "Bearer " prefix if present
            if api_key.startswith('Bearer '):
                api_key = api_key[7:]
                
        if not api_key:
            return JsonResponse({
                'error': 'API key required',
                'message': 'Please provide an API key in the X-API-Key header'
            }, status=401)
            
        try:
            # Validate API key
            api_key_obj = APIKey.objects.get(key=api_key, is_active=True)
            user = api_key_obj.user
            
            # Check if user's subscription exists and is active
            try:
                subscription = user.subscription
                if not subscription.is_active:
                    return JsonResponse({
                        'error': 'Subscription inactive',
                        'message': 'Your subscription is not active'
                    }, status=403)
            except:                # User doesn't have a subscription, create a default free one
                from accounts.models import Subscription
                subscription = Subscription.objects.create(
                    user=user,
                    plan='free',
                    is_active=True
                )
            
            # Check monthly quota
            now = timezone.now()
            current_quota, created = UsageQuota.objects.get_or_create(
                user=user,
                year=now.year,
                month=now.month,
                defaults={'usage_count': 0}
            )
            
            if current_quota.usage_count >= subscription.monthly_limit:
                return JsonResponse({
                    'error': 'Quota exceeded',
                    'message': f'Monthly limit of {subscription.monthly_limit} requests exceeded'
                }, status=429)
                  # Track usage
            APIUsage.objects.create(
                api_key=api_key_obj,
                endpoint=request.path,
                method=request.method,
                response_status=200  # We'll assume success at this point
            )
            
            # Update quota usage
            current_quota.usage_count += 1
            current_quota.save()
            
            # Update API key last used
            api_key_obj.last_used = timezone.now()
            api_key_obj.save(update_fields=['last_used'])
            
            # Add user to request for use in views
            request.api_user = user
            request.api_key = api_key_obj
            
            return None
            
        except APIKey.DoesNotExist:
            return JsonResponse({
                'error': 'Invalid API key',
                'message': 'The provided API key is invalid or inactive'
            }, status=401)
        except Exception as e:
            return JsonResponse({
                'error': 'Authentication error',
                'message': f'An error occurred during authentication: {str(e)}'
            }, status=500)
    
    def get_client_ip(self, request):
        """Get the client's IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
