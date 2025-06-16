# Authentication views
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.db.models import Count, Q
from datetime import datetime, timedelta
import json

from .models import User, APIKey, Subscription, APIUsage, UsageQuota
from .forms import CustomUserCreationForm, LoginForm


def signup_view(request):
    """User registration view"""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Note: Default subscription is created automatically via signals
            
            # Login the user
            username = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                messages.success(request, 'Account created successfully!')
                
                # Check if user selected a plan
                plan = request.GET.get('plan', 'free')
                if plan != 'free':
                    return redirect(f'/subscribe/{plan}/')
                
                return redirect('/dashboard/')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'auth/signup.html', {'form': form})


def login_view(request):
    """User login view"""
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            
            # Try to authenticate with email
            try:
                user = User.objects.get(email=email)
                user = authenticate(request, username=user.username, password=password)
            except User.DoesNotExist:
                user = None
            
            if user:
                login(request, user)
                next_url = request.GET.get('next', '/dashboard/')
                return redirect(next_url)
            else:
                messages.error(request, 'Invalid email or password.')
    else:
        form = LoginForm()
    
    return render(request, 'auth/login.html', {'form': form})


@login_required
def dashboard_view(request):
    """User dashboard with API keys and usage stats"""
    user = request.user
    
    # Get API keys
    api_keys = user.api_keys.filter(is_active=True).order_by('-created_at')
    
    # Get current month usage
    now = timezone.now()
    current_quota, _ = UsageQuota.objects.get_or_create(
        user=user,
        year=now.year,
        month=now.month
    )
    
    # Calculate usage percentage
    monthly_limit = user.subscription.monthly_limit
    usage_percentage = (current_quota.usage_count / monthly_limit) * 100 if monthly_limit > 0 else 0
    
    # Get recent API requests
    recent_requests = APIUsage.objects.filter(
        api_key__user=user
    ).order_by('-timestamp')[:10]
    
    context = {
        'api_keys': api_keys,
        'api_keys_count': api_keys.count(),
        'usage_this_month': current_quota.usage_count,
        'usage_percentage': min(usage_percentage, 100),
        'recent_requests': recent_requests,
    }
    
    return render(request, 'dashboard/dashboard.html', context)


@login_required
@require_http_methods(["POST"])
def create_api_key(request):
    """Create a new API key"""
    try:
        data = json.loads(request.body)
        name = data.get('name', '').strip()
        
        if not name:
            return JsonResponse({'error': 'Key name is required'}, status=400)
          # Check if user already has maximum number of keys
        max_keys = 1 if request.user.subscription.plan == 'free' else 20
        if request.user.api_keys.filter(is_active=True).count() >= max_keys:
            return JsonResponse({
                'error': f'Maximum number of API keys ({max_keys}) reached for your plan'
            }, status=400)
        
        api_key = APIKey.objects.create(
            user=request.user,
            name=name
        )
        
        return JsonResponse({
            'success': True,
            'key': {
                'id': api_key.id,
                'name': api_key.name,
                'key': api_key.key,  # Only return full key on creation
                'key_preview': api_key.key_preview,
                'created_at': api_key.created_at.strftime('%B %d, %Y'),
                'last_used': None
            }
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["DELETE", "POST"])
def delete_api_key(request, key_id):
    """Delete an API key"""
    try:
        api_key = APIKey.objects.get(id=key_id, user=request.user)
        api_key.is_active = False
        api_key.save()
        
        return JsonResponse({'success': True, 'message': 'API key deleted successfully'})
        
    except APIKey.DoesNotExist:
        return JsonResponse({'error': 'API key not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def pricing_view(request):
    """Pricing page"""
    return render(request, 'pricing/pricing.html')


@login_required
def subscribe_view(request, plan):
    """Handle subscription upgrades"""
    valid_plans = ['developer', 'business']
    
    if plan not in valid_plans:
        messages.error(request, 'Invalid subscription plan.')
        return redirect('/pricing/')
    
    # For now, just update the subscription
    # In production, this would integrate with Stripe
    subscription = request.user.subscription
    subscription.plan = plan
    subscription.save()
    
    messages.success(request, f'Successfully upgraded to {plan.title()} plan!')
    return redirect('/dashboard/')


@login_required
def downgrade_view(request, plan):
    """Handle subscription downgrades"""
    valid_plans = ['free']
    
    if plan not in valid_plans:
        messages.error(request, 'Invalid downgrade plan.')
        return redirect('/pricing/')
    
    current_subscription = request.user.subscription
    
    # Check if user is already on the requested plan
    if current_subscription.plan == plan:
        messages.info(request, f'You are already on the {plan.title()} plan.')
        return redirect('/dashboard/')
    
    # Only allow POST requests with confirmation
    if request.method == 'POST' and request.POST.get('confirm') == 'yes':
        # Perform the downgrade
        old_plan = current_subscription.plan.title()
        current_subscription.plan = plan
        current_subscription.save()
        
        messages.success(request, f'Successfully downgraded from {old_plan} to {plan.title()} plan. Your API limit is now {current_subscription.monthly_limit:,} calls per month.')
        return redirect('/dashboard/')
    else:
        # For GET requests or POST without confirmation, redirect to pricing with warning
        if request.method == 'GET':
            current_plan = current_subscription.plan.title()
            messages.warning(request, f'To downgrade from {current_plan} to {plan.title()}, please use the downgrade button on the pricing page.')
        else:
            messages.error(request, 'Downgrade confirmation is required.')
        return redirect('/pricing/')


@login_required
def account_settings_view(request):
    """Account settings page"""
    if request.method == 'POST':
        # Handle form submission
        user = request.user
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.company = request.POST.get('company', '')
        user.save()
        
        messages.success(request, 'Account settings updated successfully!')
        return redirect('/account/settings/')
    
    return render(request, 'account/settings.html')


def logout_view(request):
    """Custom logout view that handles both GET and POST requests"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('/')


# API Authentication middleware
from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from django.utils import timezone


class APIKeyAuthenticationMiddleware(MiddlewareMixin):
    """Middleware to authenticate API requests using API keys"""
    
    def process_request(self, request):
        # Only apply to API endpoints
        if not request.path.startswith('/api/'):
            return None
        
        # Skip authentication for documentation
        if 'swagger' in request.path or 'redoc' in request.path:
            return None
        
        # Get API key from headers
        api_key = request.META.get('HTTP_X_API_KEY') or request.GET.get('api_key')
        
        if not api_key:
            return JsonResponse({
                'error': 'API key required',
                'message': 'Include your API key in the X-API-Key header or as a query parameter'
            }, status=401)
        
        try:
            key_obj = APIKey.objects.get(key=api_key, is_active=True)
            
            # Check subscription status
            if not key_obj.user.subscription.is_active:
                return JsonResponse({
                    'error': 'Subscription inactive',
                    'message': 'Your subscription is not active. Please check your billing.'
                }, status=403)
            
            # Check usage quota
            now = timezone.now()
            quota, _ = UsageQuota.objects.get_or_create(
                user=key_obj.user,
                year=now.year,
                month=now.month
            )
            
            monthly_limit = key_obj.user.subscription.monthly_limit
            if quota.usage_count >= monthly_limit:
                return JsonResponse({
                    'error': 'Quota exceeded',
                    'message': f'Monthly limit of {monthly_limit} API calls exceeded. Upgrade your plan for more calls.',
                    'usage': quota.usage_count,
                    'limit': monthly_limit
                }, status=429)
            
            # Update last used and increment usage
            key_obj.last_used = now
            key_obj.save()
            
            quota.usage_count += 1
            quota.save()
            
            # Record API usage
            APIUsage.objects.create(
                api_key=key_obj,
                endpoint=request.path,
                method=request.method,
                response_status=200  # Will be updated in response if needed
            )
            
            # Attach user and api_key to request
            request.api_user = key_obj.user
            request.api_key = key_obj
            
        except APIKey.DoesNotExist:
            return JsonResponse({
                'error': 'Invalid API key',
                'message': 'The provided API key is invalid or has been deactivated'
            }, status=401)
        
        return None
