from .services import get_backend_url
from .data_types import URIPatternData
from django.conf import settings


def test_get_backend_url_without_target_path():
    """Should return the url when route doesn't have target_path"""
    path = "api/v1/example"
    expected_url = f"{settings.BACKEND_BASE_URL}{path}"
    route = URIPatternData(pattern=path, methods=("GET",), requires_auth=True, target_path='')
    url = get_backend_url(path=path, route=route)
    assert expected_url == url


def test_get_backend_url_with_target_path():
    """Should return the url when route has target_path"""
    path = "api/v1/example"
    expected_url = "https://example-test.com/"
    route = URIPatternData(pattern=path, methods=("GET",), requires_auth=True, target_path="https://example-test.com/")
    url = get_backend_url(path=path, route=route)
    assert expected_url == url
