def test_login_response_404(anon_client):
    payload = {
        "username":"test",
        "password":"12345678"
    }
    response = anon_client.post("/auth/login", json=payload)
    assert response.status_code == 404
    assert "access" not in response.json()
    assert "refresh" not in response.json()
    

def test_login_response_200(anon_client):
    payload = {
        "username":"testuser",
        "password":"12345678"
    }
    response = anon_client.post("/auth/login", json=payload)
    assert response.status_code == 200
    assert "access" in response.json()
    assert "refresh" in response.json()
    
def test_register_response_201(anon_client):
    payload = {
        "username":"aron",
        "password":"aaaaa",
    }
    response = anon_client.post("/auth/register", json=payload)
    assert response.status_code == 201
    assert "id" in response.json()
    assert "username" in response.json()
    assert "created_at" in response.json()
    
def test_register_response_400(anon_client):
    payload = {
        "username":"testuser",
        "password":"12345678"
    }
    response = anon_client.post("/auth/register", json=payload)
    assert response.status_code == 400
    assert "id" not in response.json()
    assert "username" not in response.json()
    assert "created_at" not in response.json()