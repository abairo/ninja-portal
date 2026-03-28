from urllib.parse import urlparse

from django.conf import settings

from apps.gateway.data_types import URIPatternData

from .infrastructure.http_client import create_http_session


async def introspect(access_token: str) -> dict:
    """
    Validates a Bearer token by introspecting it against the configured authentication provider.

    Args:
        access_token (str): The Bearer token to validate.

    Returns:
        dict: The introspection response containing token status and metadata.
    """
    async with create_http_session() as session:
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
    """
    Matches a request path and method against a list of active URI patterns.

    Args:
        path (str): The incoming request path.
        method (str): The HTTP method (e.g., 'GET').
        routes (tuple[URIPatternData]): List of active URI patterns.

    Returns:
        URIPatternData | None: The matching route configuration or None if no match is found.
    """
    parsed = urlparse(path)
    for route in routes:
        if route.pattern.parse(parsed.path) and method.upper() in route.methods:
            return route
    return None


def get_backend_url(path: str, route: URIPatternData) -> str:
    """
    Constructs the full backend URL for forwarding the request.

    Args:
        path (str): The incoming request path.
        route (URIPatternData): The matched route configuration.

    Returns:
        str: The full target URL.
    """
    base_url = route.upstream_base_url
    return route.target_path or f"{base_url}{path}"
