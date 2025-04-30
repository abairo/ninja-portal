from apps.gateway.data_types import URIPatternData
from urllib.parse import urlparse


def extract_token(authorization: str):
    return authorization.split(" ")[-1]


def match_route(path: str, method: str, routes: tuple[URIPatternData]) -> URIPatternData | None:
    parsed = urlparse(path)
    for route in routes:
        if route.pattern.parse(parsed.path) and method.upper() in route.methods:
            return route
    return None
