"""Acceptance tests for spec 900 (GET /todos/count). Each test names its criterion AC-900.n."""

from __future__ import annotations

from fastapi.testclient import TestClient

NOT_FOUND = {"error": {"code": "todo_not_found", "message": "This todo no longer exists"}}


def _create(client: TestClient, title: str) -> None:
    r = client.post("/todos", json={"title": title})
    assert r.status_code == 201, r.text


def test_count_three_todos(client: TestClient):  # AC-900.1
    for t in ("one", "two", "three"):
        _create(client, t)
    r = client.get("/todos/count")
    assert r.status_code == 200, r.text
    assert r.headers["content-type"].startswith("application/json")
    assert r.json() == {"count": 3}


def test_count_ignores_query_parameters(client: TestClient):  # AC-900.1
    _create(client, "one")
    _create(client, "two")
    r = client.get("/todos/count", params={"done": "true", "title": "zzz"})
    assert r.status_code == 200, r.text
    assert r.json() == {"count": 2}


def test_count_no_todos_is_zero(client: TestClient):  # AC-900.2
    r = client.get("/todos/count")
    assert r.status_code == 200, r.text
    assert r.headers["content-type"].startswith("application/json")
    body = r.json()
    assert body == {"count": 0}
    assert type(body["count"]) is int


def test_count_route_does_not_shadow_id_routes(client: TestClient):  # AC-900.2
    # the count route must exist, and PATCH/DELETE on the same path stay "unknown id"
    assert client.get("/todos/count").status_code == 200
    _create(client, "one")
    p = client.patch("/todos/count", json={"done": True})
    assert p.status_code == 404, p.text
    assert p.json() == NOT_FOUND
    d = client.delete("/todos/count")
    assert d.status_code == 404, d.text
    assert d.json() == NOT_FOUND
    assert client.get("/todos/count").json() == {"count": 1}


def test_patch_count_invalid_body_stays_422(client: TestClient):  # AC-900.2
    assert client.get("/todos/count").status_code == 200
    r = client.patch("/todos/count", json={"done": "nope"})
    assert r.status_code == 422, r.text
    assert r.json()["error"]["code"] == "invalid_request"
