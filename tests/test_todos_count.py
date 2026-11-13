"""Acceptance tests for spec 900: count todos through GET /todos/count."""

from __future__ import annotations

from fastapi.testclient import TestClient

NOT_FOUND = ("todo_not_found", "This todo no longer exists")


def assert_error(resp, status: int, err: tuple[str, str]) -> None:
    code, msg = err
    assert resp.status_code == status, resp.text
    assert resp.headers["content-type"].startswith("application/json")
    body = resp.json()
    assert set(body) == {"error"}
    assert set(body["error"]) == {"code", "message"}
    assert body["error"]["code"] == code
    assert body["error"]["message"] == msg


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


def test_count_of_no_todos(client: TestClient):  # AC-900.2
    r = client.get("/todos/count")
    assert r.status_code == 200, r.text
    assert r.headers["content-type"].startswith("application/json")
    assert r.json() == {"count": 0}


def test_count_route_does_not_shadow_id_routes(client: TestClient):  # AC-900.2
    assert client.get("/todos/count").status_code == 200
    assert_error(client.patch("/todos/count", json={"done": True}), 404, NOT_FOUND)
    assert_error(client.delete("/todos/count"), 404, NOT_FOUND)
