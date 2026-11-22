"""Acceptance tests for spec 900 (GET /todos/count). Each test names its criterion AC-900.n."""

from __future__ import annotations

from fastapi.testclient import TestClient

NOT_FOUND = {"error": {"code": "todo_not_found", "message": "This todo no longer exists"}}


def test_count_three_todos(client: TestClient):  # AC-900.1
    for title in ("a", "b", "c"):
        assert client.post("/todos", json={"title": title}).status_code == 201
    resp = client.get("/todos/count")
    assert resp.status_code == 200
    assert resp.headers["content-type"].split(";")[0].strip() == "application/json"
    assert resp.json() == {"count": 3}


def test_count_no_todos(client: TestClient):  # AC-900.2
    resp = client.get("/todos/count")
    assert resp.status_code == 200
    assert resp.json() == {"count": 0}

    patch_resp = client.patch("/todos/count", json={"done": True})
    assert patch_resp.status_code == 404
    assert patch_resp.json() == NOT_FOUND

    delete_resp = client.delete("/todos/count")
    assert delete_resp.status_code == 404
    assert delete_resp.json() == NOT_FOUND
