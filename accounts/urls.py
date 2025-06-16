# URL patterns for authentication and user management
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Authentication
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Password reset
    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='auth/password_reset.html',
        email_template_name='auth/password_reset_email.html',
        success_url='/accounts/password-reset/done/'
    ), name='password_reset'),
    
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='auth/password_reset_done.html'
    ), name='password_reset_done'),
    
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='auth/password_reset_confirm.html',
        success_url='/accounts/password-reset-complete/'
    ), name='password_reset_confirm'),
    
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='auth/password_reset_complete.html'
    ), name='password_reset_complete'),
    
    # Dashboard and account management
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('settings/', views.account_settings_view, name='settings'),
    
    # API key management
    path('api-keys/create/', views.create_api_key, name='create_api_key'),
    path('api-keys/<int:key_id>/delete/', views.delete_api_key, name='delete_api_key'),
    
    # Subscription management
    path('pricing/', views.pricing_view, name='pricing'),
    path('subscribe/<str:plan>/', views.subscribe_view, name='subscribe'),
]
