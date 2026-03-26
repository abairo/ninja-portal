from aiohttp import ClientSession
from django.http import HttpResponse, JsonResponse
from ninja import Router
from django.conf import settings
from .services import (
    introspect,
    match_route,
    get_backend_url
)
from .routing_state import get_uri_patterns
from .token_utils import extract_token


router = Router()


@router.api_operation(["GET", "POST", "PUT", "DELETE", "PATCH"], "/proxy/{path:path}")
async def proxy_request(request, path: str):
    """
    Proxies requests to the backend service based on matching URI patterns.

    This view performs the following steps:
    1. Matches the request path against active URI patterns.
    2. Validates authentication if required by the pattern.
    3. Forwards the request to the target backend URL.
    4. Returns the backend's response to the client.

    Args:
        request: The Django/Ninja request object.
        path (str): The path captured from the URL.

    Returns:
        HttpResponse | JsonResponse: The response from the backend or an error message.
    """
    method = request.method.upper()
    route = match_route(f"/{path}", method, await get_uri_patterns())

    if not route:
        return JsonResponse(
            {"error": "Path or method not allowed"}, status=403
        )
    if route.requires_auth:
        auth = request.headers.get("Authorization")
        if not auth or not auth.startswith("Bearer "):
            return JsonResponse(
                {"error": "Missing or invalid token"}, status=401
            )
        access_token = extract_token(auth)
        introspected_data = await introspect(access_token)
        if not introspected_data.get("active"):
            return JsonResponse({"detail": "Invalid token"}, status=401)

    backend_url = get_backend_url(path, route)

    headers = {
        k: v for k, v in request.headers.items()
        if k.lower() not in {"host", "content-length", "connection", "authorization"}
    }

    if route.upstream_app_token:
        prefix = route.upstream_token_prefix or "Bearer "
        headers['Authorization'] = f"{prefix} {route.upstream_app_token}"

    data = None

    if method in ("POST", "PUT", "PATCH"):
        data = request.body

    async with ClientSession() as session:
        async with session.request(
            method=method,
            url=backend_url,
            headers=headers,
            params=request.GET,
            data=data
        ) as resp:
            content = await resp.read()
            return HttpResponse(
                content,
                status=resp.status,
                content_type=resp.headers.get(
                    "Content-Type", "application/octet-stream"
                ),
            )
