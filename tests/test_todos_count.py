"""Acceptance tests for spec 900: GET /todos/count."""

from __future__ import annotations

from fastapi.testclient import TestClient

NOT_FOUND = {"error": {"code": "todo_not_found", "message": "This todo no longer exists"}}


def test_count_three_todos(client: TestClient) -> None:  # AC-900.1
    for title in ("a", "b", "c"):
        assert client.post("/todos", json={"title": title}).status_code == 201
    response = client.get("/todos/count")
    assert response.status_code == 200
    assert response.headers["content-type"].split(";")[0] == "application/json"
    assert response.json() == {"count": 3}


def test_count_no_todos(client: TestClient) -> None:  # AC-900.2
    response = client.get("/todos/count")
    assert response.status_code == 200
    assert response.json() == {"count": 0}


def test_patch_count_is_not_found(client: TestClient) -> None:  # AC-900.2
    response = client.patch("/todos/count", json={"done": True})
    assert response.status_code == 404
    assert response.json() == NOT_FOUND


def test_delete_count_is_not_found(client: TestClient) -> None:  # AC-900.2
    response = client.delete("/todos/count")
    assert response.status_code == 404
    assert response.json() == NOT_FOUND


def test_count_route_does_not_break_existing_list(client: TestClient) -> None:  # AC-900.2
    client.post("/todos", json={"title": "a"})
    assert client.get("/todos/count").status_code == 200
    assert len(client.get("/todos").json()) == 1
