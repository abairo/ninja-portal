from aiohttp import ClientSession


def create_http_session() -> ClientSession:
    return ClientSession(trust_env=True)
