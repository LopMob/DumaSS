def test_create_and_get_deputy(client):
    resp = client.post("/deputies", json={"full_name": "Иванов Иван Иванович"})
    assert resp.status_code == 201
    deputy_id = resp.json()["id"]

    resp = client.get(f"/deputies/{deputy_id}")
    assert resp.status_code == 200
    assert resp.json()["full_name"] == "Иванов Иван Иванович"


def test_get_missing_deputy_returns_404(client):
    resp = client.get("/deputies/9999")
    assert resp.status_code == 404


def test_create_deputy_validation_error(client):
    # full_name короче минимальной длины -> 422
    resp = client.post("/deputies", json={"full_name": "И"})
    assert resp.status_code == 422
