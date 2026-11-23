"""Acceptance tests for spec 900: count todos with GET /todos/count."""

from __future__ import annotations

from conftest import running
from fastapi.testclient import TestClient

NOT_FOUND = {"error": {"code": "todo_not_found", "message": "This todo no longer exists"}}


def create(client: TestClient, title: str = "Buy milk") -> dict:
    r = client.post("/todos", json={"title": title})
    assert r.status_code == 201, r.text
    return r.json()


def test_count_of_three_todos(client: TestClient):  # AC-900.1
    for title in ("a", "b", "c"):
        create(client, title)
    r = client.get("/todos/count")
    assert r.status_code == 200, r.text
    assert r.headers["content-type"].startswith("application/json")
    assert r.json() == {"count": 3}


def test_count_follows_creates_and_deletes(client: TestClient):  # AC-900.1
    a = create(client, "a")
    create(client, "b")
    assert client.get("/todos/count").json() == {"count": 2}
    assert client.delete(f"/todos/{a['id']}").status_code == 204
    r = client.get("/todos/count")
    assert r.status_code == 200, r.text
    assert r.json() == {"count": 1}


def test_count_of_no_todos(client: TestClient):  # AC-900.2
    r = client.get("/todos/count")
    assert r.status_code == 200, r.text
    assert r.headers["content-type"].startswith("application/json")
    assert r.json() == {"count": 0}


def test_count_with_never_used_database(postgres_url: str, no_db: None):  # AC-900.2
    from conftest import drop_todos

    drop_todos(postgres_url)
    with running(postgres_url) as c:
        r = c.get("/todos/count")
        assert r.status_code == 200, r.text
        assert r.json() == {"count": 0}


def test_count_does_not_shadow_id_routes(client: TestClient):  # AC-900.2
    assert client.get("/todos/count").json() == {"count": 0}
    patched = client.patch("/todos/count", json={"done": True})
    assert patched.status_code == 404, patched.text
    assert patched.headers["content-type"].startswith("application/json")
    assert patched.json() == NOT_FOUND
    deleted = client.delete("/todos/count")
    assert deleted.status_code == 404, deleted.text
    assert deleted.headers["content-type"].startswith("application/json")
    assert deleted.json() == NOT_FOUND


def test_other_endpoints_unchanged(client: TestClient):  # AC-900.2
    todo = create(client)
    assert client.get("/todos/count").json() == {"count": 1}
    assert client.get("/todos").json() == [todo]
    r = client.patch(f"/todos/{todo['id']}", json={"done": True})
    assert r.status_code == 200, r.text
    assert r.json() == {**todo, "done": True}
    assert client.get("/todos/count").json() == {"count": 1}
