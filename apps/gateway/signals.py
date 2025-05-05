from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import URIPattern
from .routing_state import update_uri_patterns_cache


@receiver([post_save, post_delete], sender=URIPattern)
async def refresh_patterns(sender, **kwargs):
    await update_uri_patterns_cache()
