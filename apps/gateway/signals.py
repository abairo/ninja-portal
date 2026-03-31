from asgiref.sync import async_to_sync
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import Upstream, URIPattern
from .routing_state import update_uri_patterns_cache


@receiver([post_save, post_delete], sender=URIPattern)
@receiver([post_save, post_delete], sender=Upstream)
def refresh_patterns(sender, **kwargs):
    async_to_sync(update_uri_patterns_cache)()
