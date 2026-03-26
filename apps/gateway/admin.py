from django.contrib import admin
from apps.gateway.models import URIPattern, Upstream


class URIPatternInline(admin.TabularInline):
    model = URIPattern
    extra = 1
    fields = (
        "pattern", "methods", "requires_auth", "target_path", "is_active"
    )


class UpstreamAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "base_url")
    search_fields = ("name", "base_url")
    inlines = [URIPatternInline]


class URIPatternAdmin(admin.ModelAdmin):
    search_fields = ("pattern",)
    list_display = (
        "id", "is_active", "pattern", "methods", "requires_auth", "upstream"
    )
    list_editable = ('is_active',)
    list_filter = ("methods", "requires_auth", "upstream")


admin.site.register(Upstream, UpstreamAdmin)
admin.site.register(URIPattern, URIPatternAdmin)
