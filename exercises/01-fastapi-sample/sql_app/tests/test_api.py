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


def test_authorize(sample_user_response, client):

    token = sample_user_response.headers["x-api-token"]
    data = sample_user_response.json()
    user_id = data["id"]

    # correct token
    response = client.get(f"/users/{user_id}", headers={"x-api-token": token})
    assert response.status_code == 200, response.text

    # incorrect token
    response = client.get(f"/users/{user_id}", headers={"x-api-token": "abc"})
    assert response.status_code == 401, response.text


def test_inclued_api_token_request(sample_user_response, client):
    token = sample_user_response.headers["x-api-token"]
    data = sample_user_response.json()
    user_id = data["id"]

    response = client.get(f"/users/{user_id}", headers={"x-api-token": token})
    assert response.status_code == 200, response.text

    # incorrect token
    response = client.get(f"/users/{user_id}")
    assert response.status_code == 401, response.text
