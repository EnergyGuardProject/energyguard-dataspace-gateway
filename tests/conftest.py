import os

import httpx
import pytest
from dotenv import load_dotenv

from dataspace_gateway.main import app

load_dotenv()


@pytest.fixture(scope="session")
def credentials():
    username = os.environ.get("DATASPACE_TEST_USERNAME")
    password = os.environ.get("DATASPACE_TEST_PASSWORD")
    if not username or not password:
        pytest.skip("DATASPACE_TEST_USERNAME/DATASPACE_TEST_PASSWORD not set in .env")
    return username, password


@pytest.fixture
async def client():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


@pytest.fixture
async def auth_headers(client, credentials):
    username, password = credentials
    resp = await client.post("/auth/login", json={"username": username, "password": password})
    assert resp.status_code == 200, f"login failed: {resp.status_code} {resp.text}"
    body = resp.json()
    print(f"\n[auth] logged in as {body['user']['username']} ({body['user']['email']})")
    return {"Authorization": f"Bearer {body['accessToken']}"}


@pytest.fixture
async def generic_business_object_id(client, auth_headers):
    """Business Object ID for the dataspace's "Generic data services" catalog entry -
    the same category other participants use for their own test offerings."""
    resp = await client.get("/offerings/catalog", headers=auth_headers)
    catalog = resp.json()
    generic = next(item for item in catalog if item["business_object_code"] == "GEN001")
    return generic["cross_platform_service_id"]
