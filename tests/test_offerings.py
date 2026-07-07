async def test_create_offering(client, auth_headers, generic_business_object_id):
    """Real (non-mocked) write against the live dataspace.

    Creates an actual, clearly-labeled Data Offering every time this test runs -
    there is no delete endpoint in the documented API, so this leaves a permanent,
    visible entry for other participants. Titled distinctly so it's identifiable.
    """
    payload = {
        "title": "EnergyGuard Gateway Test - Ignore (offering only)",
        "data_catalog_business_object_id": generic_business_object_id,
        "profile_selector": "json",
    }
    resp = await client.post("/offerings", headers=auth_headers, json=payload)
    assert resp.status_code == 200
    body = resp.json()
    assert "response" in body
    print(f"\nPASS /offerings -> created offering {body['response']}")


async def test_catalog(client, auth_headers):
    resp = await client.get("/offerings/catalog", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    print(f"\nPASS /offerings/catalog -> {len(data)} business objects available")
    for item in data:
        print(
            f"  - [{item['category_name']}] {item['business_object_name']} "
            f"({item['business_object_code']}, id={item['cross_platform_service_id']})"
        )


async def test_mine(client, auth_headers):
    resp = await client.get("/offerings/mine", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    print(f"\nPASS /offerings/mine -> {len(data)} offerings owned")
    for item in data:
        print(f"  - \"{item['title']}\" [{item['category']}] status={item['status']} id={item['cf_id']}")


async def test_available(client, auth_headers):
    resp = await client.get("/offerings/available", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    print(f"\nPASS /offerings/available -> {len(data)} offerings visible from other participants")
    for item in data:
        print(
            f"  - \"{item['title']}\" by {item['created_by_username']} ({item['email']}) "
            f"[{item['category']}] id={item['cf_id']}"
        )
