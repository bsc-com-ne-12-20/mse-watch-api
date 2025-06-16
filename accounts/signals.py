# Signals for automatic subscription creation
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Subscription

User = get_user_model()


@receiver(post_save, sender=User)
def create_user_subscription(sender, instance, created, **kwargs):
    """Create a default subscription when a user is created"""
    if created:
        Subscription.objects.get_or_create(
            user=instance,
            defaults={'plan': 'free'}
        )
