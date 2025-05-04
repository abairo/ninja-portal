from django.contrib import admin
from django.conf import settings
from apps.gateway.models import URIPattern
from .services import get_uri_patterns


class URIPatternAdmin(admin.ModelAdmin):
    search_fields = ("pattern",)
    list_display = ("id", "pattern", "methods", "requires_auth")
    list_filter = ("methods", "requires_auth")

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        settings.URI_PATTERNS = get_uri_patterns()


admin.site.register(URIPattern, URIPatternAdmin)
