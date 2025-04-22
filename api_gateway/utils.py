def extract_token(authorization: str):
    return authorization.split(" ")[-1]


def match_route(path: str, method: str, routes) -> dict | None:
    for route in routes:
        if route["pattern"].parse(path) and method.upper() in route["methods"]:
            return route
    return None
