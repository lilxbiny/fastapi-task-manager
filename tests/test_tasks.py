def test_create_and_get_task(client, auth_headers):
    headers = auth_headers()
    resp = client.post(
        "/tasks/",
        json={"title": "Write tests", "description": "Cover the API", "status": "todo"},
        headers=headers,
    )
    assert resp.status_code == 201
    task = resp.json()
    assert task["title"] == "Write tests"
    assert task["status"] == "todo"

    get_resp = client.get(f"/tasks/{task['id']}", headers=headers)
    assert get_resp.status_code == 200
    assert get_resp.json()["id"] == task["id"]


def test_list_tasks_pagination_and_filter(client, auth_headers):
    headers = auth_headers()
    for i in range(3):
        client.post(
            "/tasks/",
            json={"title": f"Task {i}", "status": "todo"},
            headers=headers,
        )
    client.post("/tasks/", json={"title": "Done task", "status": "done"}, headers=headers)

    all_resp = client.get("/tasks/", headers=headers)
    assert all_resp.status_code == 200
    assert all_resp.json()["total"] == 4

    filtered = client.get("/tasks/?status=done", headers=headers)
    assert filtered.status_code == 200
    assert filtered.json()["total"] == 1

    paged = client.get("/tasks/?skip=0&limit=2", headers=headers)
    assert len(paged.json()["items"]) == 2


def test_update_task_put_and_patch(client, auth_headers):
    headers = auth_headers()
    created = client.post(
        "/tasks/", json={"title": "Old title", "status": "todo"}, headers=headers
    ).json()

    put_resp = client.put(
        f"/tasks/{created['id']}",
        json={"title": "New title", "status": "in_progress", "description": None, "priority": "high"},
        headers=headers,
    )
    assert put_resp.status_code == 200
    assert put_resp.json()["title"] == "New title"
    assert put_resp.json()["status"] == "in_progress"

    patch_resp = client.patch(
        f"/tasks/{created['id']}", json={"status": "done"}, headers=headers
    )
    assert patch_resp.status_code == 200
    assert patch_resp.json()["status"] == "done"
    assert patch_resp.json()["title"] == "New title"  # untouched by PATCH


def test_delete_task(client, auth_headers):
    headers = auth_headers()
    created = client.post(
        "/tasks/", json={"title": "Temp", "status": "todo"}, headers=headers
    ).json()

    del_resp = client.delete(f"/tasks/{created['id']}", headers=headers)
    assert del_resp.status_code == 204

    get_resp = client.get(f"/tasks/{created['id']}", headers=headers)
    assert get_resp.status_code == 404


def test_cannot_access_other_users_task(client, auth_headers):
    owner_headers = auth_headers(email="owner@example.com")
    other_headers = auth_headers(email="intruder@example.com")

    created = client.post(
        "/tasks/", json={"title": "Private task", "status": "todo"}, headers=owner_headers
    ).json()

    resp = client.get(f"/tasks/{created['id']}", headers=other_headers)
    assert resp.status_code in (403, 404)

    resp_delete = client.delete(f"/tasks/{created['id']}", headers=other_headers)
    assert resp_delete.status_code in (403, 404)


def test_tasks_require_authentication(client):
    resp = client.get("/tasks/")
    assert resp.status_code == 401
