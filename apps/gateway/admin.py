from django.contrib import admin
from apps.gateway.models import URIPattern


class URIPatternAdmin(admin.ModelAdmin):
    search_fields = ("pattern",)
    list_display = ("id", "is_active", "pattern", "methods", "requires_auth")
    list_editable = ('is_active',)
    list_filter = ("methods", "requires_auth")


admin.site.register(URIPattern, URIPatternAdmin)
