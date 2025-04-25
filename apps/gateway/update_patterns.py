from apps.gateway.models import URIPattern, URIPatternData


def update_patterns() -> tuple[URIPatternData]:
    return tuple(
        map(lambda uri: uri.to_uri_pattern_data(), URIPattern.objects.all())
    )