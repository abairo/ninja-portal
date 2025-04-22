import os
from aiohttp import ClientSession
from django.http import HttpResponse, JsonResponse
from dotenv import load_dotenv
from ninja import Router

load_dotenv()
from .patterns import URL_PATTERNS
from .services import introspect
from .utils import extract_token, match_route

router = Router()

INTROSPECT_URL = os.getenv("KEYCLOAK_INTROSPECT_URL") or ""
CLIENT_ID = os.getenv("KEYCLOAK_CLIENT_ID")
CLIENT_SECRET = os.getenv("KEYCLOAK_CLIENT_SECRET")
BACKEND_BASE_URL = os.getenv("BACKEND_BASE_URL")
APP_TOKEN = os.getenv("APP_TOKEN")


@router.api_operation(["GET", "POST", "PUT", "DELETE", "PATCH"], "/proxy/{path:path}")
async def proxy_request(request, path: str):
    method = request.method.upper()
    route = match_route(path, method, URL_PATTERNS)
    if not route:
        return JsonResponse(
            {"error": "Path or method not allowed"}, status=403
        )
    if route["requires_auth"]:
        auth = request.headers.get("Authorization")
        if not auth or not auth.startswith("Bearer "):
            return JsonResponse(
                {"error": "Missing or invalid token"}, status=401
            )
        access_token = extract_token(auth)
        introspected_data = await introspect(access_token)
        if not introspected_data.get("active"):
            return JsonResponse({"detail": "Invalid token"}, status=401)

    target_path = route["target_path"] or path
    backend_url = f"{BACKEND_BASE_URL}{target_path}"

    headers = {
        k: v for k, v in request.headers.items()
        if k.lower() not in {"host", "content-length", "connection"}
    }

    headers['Authorization'] = f"Token {APP_TOKEN}"

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
