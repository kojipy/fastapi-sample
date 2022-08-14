def test_create_user(test_db, client):
    response = client.post(
        "/users/",
        json={"email": "deadpool@example.com", "password": "chimichangas4life"},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["email"] == "deadpool@example.com"
    assert "id" in data
    user_id = data["id"]
    assert "x-api-token" in response.headers.keys()

    token = response.headers["x-api-token"]
    response = client.get(f"/users/{user_id}", headers={"x-api-token": token})
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["email"] == "deadpool@example.com"
    assert data["id"] == user_id


def test_authorize(sample_user, client):
    sample_user_response = sample_user["response"]
    token = sample_user_response.headers["x-api-token"]
    data = sample_user_response.json()
    user_id = data["id"]

    # correct token
    response = client.get(f"/users/{user_id}", headers={"x-api-token": token})
    assert response.status_code == 200, response.text

    # incorrect token
    response = client.get(f"/users/{user_id}", headers={"x-api-token": "abc"})
    assert response.status_code == 401, response.text


def test_inclued_api_token_request(sample_user, client):
    sample_user_response = sample_user["response"]
    token = sample_user_response.headers["x-api-token"]
    data = sample_user_response.json()
    user_id = data["id"]

    response = client.get(f"/users/{user_id}", headers={"x-api-token": token})
    assert response.status_code == 200, response.text

    # incorrect token
    response = client.get(f"/users/{user_id}")
    assert response.status_code == 401, response.text


def test_create_items(sample_user, client):
    sample_user_response = sample_user["response"]
    token = sample_user_response.headers["x-api-token"]
    data = sample_user_response.json()
    user_id = data["id"]

    response = client.post(
        f"/users/{user_id}/items/",
        headers={"x-api-token": token},
        json={"title": "sample-task", "descripthion": "This is Sample task"},
    )

    assert response.status_code == 200, response.text


def test_login(sample_user, client):
    sample_user_response = sample_user["response"]
    data = sample_user_response.json()
    email = data["email"]
    password = sample_user["password"]
    user_id = data["id"]

    response = client.post("/login/", json={"email": email, "password": password})
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["email"] == email
    assert data["id"] == user_id


def test_my_items(sample_user, client):
    sample_user_response = sample_user["response"]
    token = sample_user_response.headers["x-api-token"]
    data = sample_user_response.json()
    user_id = data["id"]

    # create item
    item_create = {"title": "sample-task", "description": "This is Sample task"}
    response = client.post(
        f"/users/{user_id}/items/", headers={"x-api-token": token}, json=item_create
    )
    assert response.status_code == 200, response.text

    response = client.get("/me/items", headers={"x-api-token": token})
    assert response.status_code == 200, response.text
    items = response.json()

    assert items[0]["title"] == item_create["title"]
    assert items[0]["description"] == item_create["description"]
    assert items[0]["id"] == user_id
    assert items[0]["owner_id"] == user_id


def test_delete_user(sample_user, client):
    sample_user_response = sample_user["response"]
    token = sample_user_response.headers["x-api-token"]
    data = sample_user_response.json()
    user_id = data["id"]

    response = client.delete(
        f"/users/{user_id}/delete/", headers={"x-api-token": token}
    )
    assert response.status_code == 200, response.text

    response_users = client.get("/users/", headers={"x-api-token": token})
    sample_user = response_users.json()[0]
    assert sample_user["email"] == data["email"]
    assert not sample_user["is_active"]
