from aiohttp import ClientSession
from django.http import HttpResponse, JsonResponse
from ninja import Router
from django.conf import settings
from .services import introspect
from .utils import (
    extract_token,
    match_route,
    get_backend_url
)

router = Router()


@router.api_operation(["GET", "POST", "PUT", "DELETE", "PATCH"], "/proxy/{path:path}")
async def proxy_request(request, path: str):
    method = request.method.upper()
    route = match_route(f"/{path}", method, settings.URI_PATTERNS)

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
        if k.lower() not in {"host", "content-length", "connection"}
    }

    headers['Authorization'] = f"Token {settings.APP_TOKEN}"

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
