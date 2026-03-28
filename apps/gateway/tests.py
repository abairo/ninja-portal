from asgiref.sync import sync_to_async
import pytest

from .data_types import URIPatternData
from .infrastructure.http_client import create_http_session
from .models import URIPattern, Upstream
from .routing_state import get_uri_patterns
from .services import get_backend_url
from .token_utils import extract_token

ROUTES = [
    {"pattern": "/api/v1/my-example/{id}/example_1", "methods": ("GET",), "requires_auth": True, "target_path": ""},
    {"pattern": "/api/v1/my-example/{id}/example_2", "methods": ("GET",), "requires_auth": True, "target_path": ""},
    {"pattern": "/api/v1/my-example/{id}/example_3", "methods": ("GET",), "requires_auth": True, "target_path": ""},
    {"pattern": "/api/v1/my-example/{id}/example4", "methods": ("GET",), "requires_auth": True, "target_path": ""},
]


@pytest.fixture
def uri_patterns(db) -> list[URIPattern]:
    return [URIPattern.objects.create(**route) for route in ROUTES]


def test_get_backend_url_without_target_path():
    """Should return the url when route doesn't have target_path (using upstream base url)"""
    path = "api/v1/example"
    expected_url = f"http://mock-upstream.com/{path}"
    route = URIPatternData(
        pattern=path,
        methods=("GET",),
        requires_auth=True,
        target_path='',
        upstream_base_url="http://mock-upstream.com/"
    )
    url = get_backend_url(path=path, route=route)
    assert expected_url == url


def test_get_backend_url_with_target_path():
    """Should return the url when route has target_path"""
    path = "api/v1/example"
    expected_url = "https://example-test.com/"
    route = URIPatternData(pattern=path, methods=("GET",), requires_auth=True, target_path="https://example-test.com/")
    url = get_backend_url(path=path, route=route)
    assert expected_url == url


@pytest.mark.parametrize(
    "test_input, expected_output",
    [
        ("Bearer my_token", "my_token"),
        ("Token my_token", "my_token"),
        (" Bearer my_token ", "my_token")
    ]
)
def test_extract_token(test_input, expected_output):
    """Shoud return a extracted token"""
    assert expected_output == extract_token(test_input)


@pytest.mark.django_db
def test_get_uri_patterns(uri_patterns: URIPattern):
    assert get_uri_patterns()


@pytest.mark.asyncio
@pytest.mark.django_db
async def test_cache_refreshed_on_upstream_change():
    """Should refresh cache when an upstream is updated"""
    upstream = await sync_to_async(Upstream.objects.create)(
        name="Test Upstream",
        base_url="http://old-url.com"
    )
    await sync_to_async(URIPattern.objects.create)(
        pattern="/test",
        methods="GET",
        upstream=upstream,
        is_active=True
    )

    patterns = await get_uri_patterns()
    assert patterns[0].upstream_base_url == "http://old-url.com/"

    upstream.base_url = "http://new-url.com"
    await sync_to_async(upstream.save)()

    patterns = await get_uri_patterns()
    assert patterns[0].upstream_base_url == "http://new-url.com/"


@pytest.mark.asyncio
async def test_create_http_session_uses_env_proxy_settings():
    session = create_http_session()
    try:
        assert session.trust_env is True
    finally:
        await session.close()
