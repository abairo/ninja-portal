import os
from dotenv import load_dotenv
from aiohttp import ClientSession

load_dotenv()

INTROSPECT_URL = os.getenv("KEYCLOAK_INTROSPECT_URL") or ""
CLIENT_ID = os.getenv("KEYCLOAK_CLIENT_ID")
CLIENT_SECRET = os.getenv("KEYCLOAK_CLIENT_SECRET")
BACKEND_BASE_URL = os.getenv("BACKEND_BASE_URL")
APP_TOKEN = os.getenv("APP_TOKEN")


async def introspect(access_token: str) -> dict:
    async with ClientSession() as session:
        async with session.post(
            INTROSPECT_URL,
            data={
                "token": access_token,
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
            },
        ) as response:
            return await response.json()
