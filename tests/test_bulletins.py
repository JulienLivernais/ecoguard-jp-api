def test_create_bulletin(client):
    response = client.post("/bulletins", json={
        "date_start": "2026-07-06T00:00:00",
        "date_end": "2026-07-06T23:59:59"
    })
    assert response.status_code == 200
    assert "task_id" in response.json()

