# Admin configuration for accounts app
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Subscription, APIKey, APIUsage, UsageQuota


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom user admin"""
    list_display = ('email', 'first_name', 'last_name', 'company', 'is_active', 'date_joined')
    list_filter = ('is_active', 'is_staff', 'date_joined')
    search_fields = ('email', 'first_name', 'last_name', 'company')
    ordering = ('-date_joined',)
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('company',)}),
    )


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """Subscription admin"""
    list_display = ('user', 'plan', 'is_active', 'monthly_limit', 'price', 'created_at')
    list_filter = ('plan', 'is_active', 'created_at')
    search_fields = ('user__email', 'user__first_name', 'user__last_name')
    readonly_fields = ('created_at', 'updated_at')
    
    def monthly_limit(self, obj):
        return f"{obj.monthly_limit:,}"
    monthly_limit.short_description = 'Monthly Limit'
    
    def price(self, obj):
        return f"${obj.price}"
    price.short_description = 'Price'


@admin.register(APIKey)
class APIKeyAdmin(admin.ModelAdmin):
    """API Key admin"""
    list_display = ('name', 'user', 'key_preview', 'is_active', 'last_used', 'created_at')
    list_filter = ('is_active', 'created_at', 'last_used')
    search_fields = ('name', 'user__email', 'key')
    readonly_fields = ('key', 'created_at')
    
    def key_preview(self, obj):
        return obj.key_preview
    key_preview.short_description = 'Key Preview'


@admin.register(APIUsage)
class APIUsageAdmin(admin.ModelAdmin):
    """API Usage admin"""
    list_display = ('api_key', 'endpoint', 'method', 'response_status', 'timestamp')
    list_filter = ('method', 'response_status', 'timestamp')
    search_fields = ('api_key__user__email', 'endpoint')
    readonly_fields = ('timestamp',)
    date_hierarchy = 'timestamp'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('api_key__user')


@admin.register(UsageQuota)
class UsageQuotaAdmin(admin.ModelAdmin):
    """Usage Quota admin"""
    list_display = ('user', 'year', 'month', 'usage_count', 'monthly_limit', 'usage_percentage')
    list_filter = ('year', 'month')
    search_fields = ('user__email',)
    readonly_fields = ('created_at', 'updated_at')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user__subscription')
    
    def monthly_limit(self, obj):
        return f"{obj.user.subscription.monthly_limit:,}"
    monthly_limit.short_description = 'Monthly Limit'
    
    def usage_percentage(self, obj):
        limit = obj.user.subscription.monthly_limit
        if limit > 0:
            percentage = (obj.usage_count / limit) * 100
            return f"{percentage:.1f}%"
        return "N/A"
    usage_percentage.short_description = 'Usage %'
