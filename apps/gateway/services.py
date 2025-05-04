from django.conf import settings
from aiohttp import ClientSession
from apps.gateway.models import URIPattern
from apps.gateway.data_types import URIPatternData
from urllib.parse import urlparse


async def introspect(access_token: str) -> dict:
    async with ClientSession() as session:
        async with session.post(
            settings.INTROSPECT_URL,
            data={
                "token": access_token,
                "client_id": settings.CLIENT_ID,
                "client_secret": settings.CLIENT_SECRET,
            },
        ) as response:
            return await response.json()


def match_route(path: str, method: str, routes: tuple[URIPatternData]) -> URIPatternData | None:
    parsed = urlparse(path)
    for route in routes:
        if route.pattern.parse(parsed.path) and method.upper() in route.methods:
            return route
    return None


def get_backend_url(path: str, route: URIPatternData) -> str:
    return route.target_path or f"{settings.BACKEND_BASE_URL}{path}"


def update_patterns() -> tuple[URIPatternData]:
    return tuple(
        map(lambda uri: uri.to_uri_pattern_data(), URIPattern.objects.all())
    )


def get_uri_patterns() -> tuple[URIPatternData]:
    return settings.URL_URI_PATTERNS or update_patterns()
