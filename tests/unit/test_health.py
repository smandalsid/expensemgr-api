

def test_root(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"Message": "Application looks healthy"}
