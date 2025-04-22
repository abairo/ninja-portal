import os

# import httpx
from aiohttp import ClientSession, FormData
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


@router.get("/proxy/hello-world")
async def hello_world(request, *args, **kwargs):
    print("path:", kwargs)
    token = extract_token(request)
    data = await introspect(token)
    print(data)
    return JsonResponse(data, status=200)


@router.api_operation(["GET", "POST", "PUT", "DELETE", "PATCH"], "/proxy/{path:path}")
async def proxy_request(request, path: str):
    method = request.method.upper()
    content_type = request.headers.get("Content-Type", "").lower()

    route = match_route(path, method, URL_PATTERNS)
    if not route:
        return JsonResponse({"error": "Path or method not allowed"}, status=403)

    if route["requires_auth"]:
        auth = request.headers.get("Authorization")
        if not auth or not auth.startswith("Bearer "):
            return JsonResponse({"error": "Missing or invalid token"}, status=401)
        access_token = extract_token(auth)
        introspected_data = await introspect(access_token)
        breakpoint();
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
    json_data = None

    if method in ("POST", "PUT", "PATCH"):
        if content_type.startswith("multipart/form-data"):
            form = FormData()
            for key, value in request.POST.items():
                form.add_field(key, value)
            for file_key, uploaded_file in request.FILES.items():
                form.add_field(
                    file_key,
                    uploaded_file.file,
                    filename=uploaded_file.name,
                    content_type=uploaded_file.content_type,
                )
            data = form

        elif content_type.startswith("application/json"):
            body = await request.body()
            json_data = body.decode()

        elif content_type.startswith("text/plain"):
            body = await request.body()
            data = body.decode()

        else:
            data = await request.body()
    
    async with ClientSession() as session:
        async with session.request(
            method=method,
            url=backend_url,
            headers=headers,
            params=request.GET,
            data=data,
            json=json_data,
        ) as resp:
            content = await resp.read()
            return HttpResponse(
                content,
                status=resp.status,
                content_type=resp.headers.get("Content-Type", "application/octet-stream"),
            )
