from asgiref.sync import sync_to_async
from django.core.cache import cache

from .data_types import URIPatternData
from .models import URIPattern


_route_cache: tuple[URIPatternData] | None = None


@sync_to_async
def load_uri_patterns() -> tuple[URIPatternData]:
    uri_patterns = URIPattern.objects.filter(is_active=True)
    return tuple(
        map(lambda uri: uri.to_uri_pattern_data(), uri_patterns)
    )


async def update_uri_patterns_cache() -> tuple[URIPatternData]:
    route_patterns = await load_uri_patterns()
    cache.set('uri_patterns', route_patterns)
    return route_patterns


async def get_uri_patterns():
    route_patterns = cache.get('uri_patterns')
    if route_patterns is None:
        return await update_uri_patterns_cache()
    return route_patterns
