from django.apps import AppConfig
from django.conf import settings


class GatewayConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.gateway"

    def ready(self):
        from .update_patterns import update_patterns
        settings.URI_PATTERNS = update_patterns()
        super().ready()
