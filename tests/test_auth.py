async def test_login(client, credentials):
    username, password = credentials
    resp = await client.post("/auth/login", json={"username": username, "password": password})
    assert resp.status_code == 200
    body = resp.json()
    assert "accessToken" in body
    assert body["user"]["username"]
    print(f"PASS /auth/login -> logged in as {body['user']['username']} ({body['user']['email']})")
