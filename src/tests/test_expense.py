def test_get_user_expense_403(anon_client):
    response = anon_client.get("/expense")
    assert response.status_code == 403

def test_get_user_expense_200(auth_client):
    response = auth_client.get("/expense")
    assert response.status_code == 200
    assert len(response.json()) > 0
    assert len(response.json()) <= 3

    
def test_expense_detail_response_200(auth_client, random_expense):
    expense_obj = random_expense
    response = auth_client.get(f"/expense/{expense_obj.id}")
    assert response.status_code == 200


def test_expense_detail_response_404(auth_client):
    response = auth_client.get(f"/expense/1000")
    assert response.status_code == 404
    assert "detail" in response.json()
    assert response.json()['error_raised'] == True
    
def test_expense_delete_200(auth_client, random_expense):
    expense_obj = random_expense
    response = auth_client.delete(f"/expense/{expense_obj.id}")
    assert response.status_code == 200

def test_expense_delete_404(auth_client):
    response = auth_client.delete(f"/expense/4")
    assert response.status_code == 404
    assert "detail" in response.json()
    assert response.json()['error_raised'] == True
    
def test_expense_delete_403(anon_client):
    response = anon_client.delete(f"/expense/10")
    assert response.status_code == 403
    assert "detail" in response.json()
    assert response.json()['error_raised'] == True