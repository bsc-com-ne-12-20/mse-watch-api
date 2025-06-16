# Authentication and API management models
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
import secrets
import string


class User(AbstractUser):
    """Extended user model with additional fields"""
    company = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.email or self.username


class Subscription(models.Model):
    """User subscription model"""
    PLAN_CHOICES = [
        ('free', 'Free'),
        ('developer', 'Developer'),
        ('business', 'Business'),
    ]
    
    PLAN_LIMITS = {
        'free': 1000,
        'developer': 50000,
        'business': 500000,
    }
    
    PLAN_PRICES = {
        'free': 0,
        'developer': 49,
        'business': 199,
    }
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='subscription')
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES, default='free')
    is_active = models.BooleanField(default=True)
    stripe_subscription_id = models.CharField(max_length=200, blank=True, null=True)
    next_billing_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    @property
    def monthly_limit(self):
        return self.PLAN_LIMITS.get(self.plan, 1000)
    
    @property
    def price(self):
        return self.PLAN_PRICES.get(self.plan, 0)
    
    def get_current_quota(self):
        """Get or create the current month's usage quota"""
        now = timezone.now()
        quota, created = UsageQuota.objects.get_or_create(
            user=self.user,
            year=now.year,
            month=now.month,
            defaults={'usage_count': 0}
        )
        return quota
    
    def __str__(self):
        return f"{self.user.email} - {self.plan}"


class APIKey(models.Model):
    """API key model for authentication"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='api_keys')
    name = models.CharField(max_length=100)
    key = models.CharField(max_length=64, unique=True)
    is_active = models.BooleanField(default=True)
    last_used = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        super().save(*args, **kwargs)
    
    @staticmethod
    def generate_key():
        """Generate a secure API key"""
        alphabet = string.ascii_letters + string.digits
        return 'mse_' + ''.join(secrets.choice(alphabet) for _ in range(40))
    
    @property
    def key_preview(self):
        """Return a preview of the key for display purposes"""
        return f"{self.key[:8]}...{self.key[-8:]}"
    
    def __str__(self):
        return f"{self.name} ({self.user.email})"


class APIUsage(models.Model):
    """Track API usage for billing and analytics"""
    api_key = models.ForeignKey(APIKey, on_delete=models.CASCADE, related_name='usage_records')
    endpoint = models.CharField(max_length=200)
    method = models.CharField(max_length=10)
    response_status = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['api_key', 'timestamp']),
            models.Index(fields=['timestamp']),
        ]
    
    def __str__(self):
        return f"{self.api_key.user.email} - {self.endpoint} - {self.timestamp}"


class UsageQuota(models.Model):
    """Monthly usage tracking"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='usage_quotas')
    year = models.IntegerField()
    month = models.IntegerField()
    usage_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'year', 'month']
        indexes = [
            models.Index(fields=['user', 'year', 'month']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.year}/{self.month:02d} - {self.usage_count}"
