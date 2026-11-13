"""Acceptance tests for spec 900 (GET /todos/count). Each test names its criterion AC-900.n."""

from __future__ import annotations

from fastapi.testclient import TestClient

NOT_FOUND = {"error": {"code": "todo_not_found", "message": "This todo no longer exists"}}


def test_count_three_todos(client: TestClient):  # AC-900.1
    for title in ("one", "two", "three"):
        assert client.post("/todos", json={"title": title}).status_code == 201
    r = client.get("/todos/count")
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("application/json")
    assert r.json() == {"count": 3}


def test_count_no_todos(client: TestClient):  # AC-900.2
    r = client.get("/todos/count")
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("application/json")
    assert r.json() == {"count": 0}


def test_count_does_not_shadow_id_routes(client: TestClient):  # AC-900.2
    # The count route must exist (GET answers 200) while PATCH/DELETE still treat
    # "count" as an unknown id.
    assert client.get("/todos/count").status_code == 200
    patched = client.patch("/todos/count", json={"done": True})
    assert patched.status_code == 404
    assert patched.json() == NOT_FOUND
    deleted = client.delete("/todos/count")
    assert deleted.status_code == 404
    assert deleted.json() == NOT_FOUND
