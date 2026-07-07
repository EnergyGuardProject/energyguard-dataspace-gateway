import pytest


async def test_consumed(client, auth_headers):
    resp = await client.get("/data/consumed", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    print(f"\nPASS /data/consumed -> {len(data)} data entities consumed")
    for item in data:
        print(
            f"  - \"{item['data_title']}\" file={item['file_name']} "
            f"from offering \"{item['offering_title']}\" by {item['provider_username']} "
            f"({item['provider_company_name']}) on {item['created_on']}"
        )


async def test_download_consumed(client, auth_headers):
    """Real download of an already-consumed entity; skips cleanly if none exist yet."""
    list_resp = await client.get("/data/consumed", headers=auth_headers)
    entities = list_resp.json()
    if not entities:
        pytest.skip("No consumed Data Entities yet - nothing to test /data/consumed/{id} against")

    entity = entities[0]
    resp = await client.get(
        f"/data/consumed/{entity['id']}", headers=auth_headers, params={"filename": entity["file_name"]}
    )
    assert resp.status_code == 200
    assert resp.headers["content-disposition"] == f'attachment; filename="{entity["file_name"]}"'
    print(
        f"\nPASS /data/consumed/{entity['id']} -> {len(resp.content)} bytes, "
        f"content-type={resp.headers['content-type']}"
    )
    print(f"  preview: {resp.content[:120]!r}")


async def test_provide_data(client, auth_headers, generic_business_object_id):
    """Real (non-mocked) round trip against the live dataspace: creates its own
    test Data Offering, then uploads a small text file to it. Self-contained
    (doesn't depend on any pre-existing owned offering, or on other tests' order) -
    but like test_create_offering, this leaves a permanent, visible offering behind.
    """
    create_resp = await client.post(
        "/offerings",
        headers=auth_headers,
        json={
            "title": "EnergyGuard Gateway Test - Ignore (provide-data)",
            "data_catalog_business_object_id": generic_business_object_id,
            "profile_selector": "json",
        },
    )
    assert create_resp.status_code == 200
    data_offering_id = create_resp.json()["response"]
    print(f"\n[setup] created offering {data_offering_id} for /data/provide test")

    payload = {
        "title": "EnergyGuard gateway test upload",
        "description": "Automated test upload from the FastAPI gateway test suite",
        "filename": "message.txt",
        "file": "hello from EnergyGuard",
        "data_offering_id": data_offering_id,
    }
    resp = await client.post("/data/provide", headers=auth_headers, json=payload)
    print(f"/data/provide -> HTTP {resp.status_code}: {resp.text[:200]}")
    assert resp.status_code == 200
    body = resp.json()
    assert "id" in body
    print(f"PASS /data/provide -> created entity {body['id']}")
