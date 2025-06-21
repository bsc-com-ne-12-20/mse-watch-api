#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from accounts.models import APIKey, User

# Check if your API key exists
api_key = "mse_5PFAyspVWQnz33boHidjCIiU2y6aNoEmzZteXzRV"
print(f"Looking for API key: {api_key}")

try:
    key_obj = APIKey.objects.get(key=api_key)
    print(f"✅ API key found!")
    print(f"   User: {key_obj.user.email}")
    print(f"   Active: {key_obj.is_active}")
    print(f"   Created: {key_obj.created_at}")
    print(f"   Last used: {key_obj.last_used}")
    
    # Check user subscription
    print(f"   Subscription: {key_obj.user.subscription.plan}")
    print(f"   Subscription active: {key_obj.user.subscription.is_active}")
    
except APIKey.DoesNotExist:
    print("❌ API key not found in database")
    print("Available API keys:")
    for key in APIKey.objects.all():
        print(f"   {key.key[:20]}... (User: {key.user.email})")

except Exception as e:
    print(f"❌ Error: {e}")
