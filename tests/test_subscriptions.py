async def test_my_subscriptions(client, auth_headers):
    resp = await client.get("/subscriptions/mine", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    print(f"\nPASS /subscriptions/mine -> {len(data)} subscriptions")
    for item in data:
        print(
            f"  - \"{item['title']}\" [{item['category_name']}] "
            f"status={item['status']} subscription_id={item['my_subscription_id']}"
        )


async def test_incoming_requests(client, auth_headers):
    resp = await client.get("/subscriptions/requests", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    print(f"\nPASS /subscriptions/requests -> {len(data)} requests received on my offerings")
    for item in data:
        print(
            f"  - \"{item['title']}\" requested by {item['user_requesting']} "
            f"status={item['status']} request_id={item['request_id']}"
        )
