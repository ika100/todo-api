"""Acceptance tests for spec 001 (todo REST API). Each test names its criterion AC-001.n."""

from __future__ import annotations

import re
import time
import uuid

import pytest
from fastapi.testclient import TestClient

from conftest import UNREACHABLE_URL, drop_todos, make_app, running

TS_RE = re.compile(r"^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d\.\d{3}Z$")
UNAVAILABLE = {
    "error": {"code": "unavailable", "message": "Todos are unavailable, please try again"}
}
NOT_FOUND = {"error": {"code": "todo_not_found", "message": "This todo no longer exists"}}


def assert_error(resp, status: int, code: str, message: str | None = None) -> None:
    assert resp.status_code == status, resp.text
    assert resp.headers["content-type"].startswith("application/json")
    body = resp.json()
    assert set(body) == {"error"}
    assert set(body["error"]) == {"code", "message"}
    assert body["error"]["code"] == code
    if message is None:
        assert body["error"]["message"]
    else:
        assert body["error"]["message"] == message


def create(client: TestClient, title: str = "Buy milk") -> dict:
    r = client.post("/todos", json={"title": title})
    assert r.status_code == 201, r.text
    return r.json()


def post_raw(client: TestClient, raw: bytes):
    return client.post("/todos", content=raw, headers={"Content-Type": "application/json"})


def patch_raw(client: TestClient, todo_id: str, raw: bytes):
    return client.patch(
        f"/todos/{todo_id}", content=raw, headers={"Content-Type": "application/json"}
    )


# ---------------------------------------------------------------- AC-001.1 / .2


def test_list_empty_returns_empty_array(client: TestClient):  # AC-001.1
    r = client.get("/todos")
    assert r.status_code == 200
    assert r.json() == []


def test_list_three_ordered_with_exact_fields(client: TestClient):  # AC-001.2
    created = [create(client, t) for t in ("one", "two", "three")]
    r = client.get("/todos")
    assert r.status_code == 200
    items = r.json()
    assert len(items) == 3
    for item in items:
        assert set(item) == {"id", "title", "done", "created_at"}
    assert [i["title"] for i in items] == ["one", "two", "three"]
    assert [i["id"] for i in items] == [c["id"] for c in created]
    keys = [(i["created_at"], i["id"]) for i in items]
    assert keys == sorted(keys)


# ---------------------------------------------------------------- AC-001.3 / .4


def test_create_returns_todo(client: TestClient):  # AC-001.3
    first = create(client, "Other")
    r = client.post("/todos", json={"title": "Buy milk"})
    assert r.status_code == 201
    body = r.json()
    assert set(body) == {"id", "title", "done", "created_at"}
    parsed = uuid.UUID(body["id"])
    assert parsed.version == 4
    assert body["id"] == str(parsed)
    assert body["id"] != first["id"]
    assert body["title"] == "Buy milk"
    assert body["done"] is False
    assert TS_RE.match(body["created_at"])
    listed = client.get("/todos").json()
    assert listed[-1] == body


def test_create_trims_whitespace_keeps_inner(client: TestClient):  # AC-001.4
    r = client.post("/todos", json={"title": "  Buy milk\t\n"})
    assert r.status_code == 201
    assert r.json()["title"] == "Buy milk"
    assert client.get("/todos").json()[0]["title"] == "Buy milk"
    inner = client.post("/todos", json={"title": "Buy  milk"})
    assert inner.status_code == 201
    assert inner.json()["title"] == "Buy  milk"


# ---------------------------------------------------------------- AC-001.5 / .6 / .7 / .8


@pytest.mark.parametrize(
    "body",
    [b"{}", b'{"title": null}', b'{"title": ""}', b'{"title": "   "}', b'{"title": " \\t\\n "}'],
)
def test_create_title_required(client: TestClient, body: bytes):  # AC-001.5
    r = post_raw(client, body)
    assert_error(r, 422, "title_required", "Title is required")
    assert client.get("/todos").json() == []


@pytest.mark.parametrize("char", ["a", "é"])
def test_create_title_too_long(client: TestClient, char: str):  # AC-001.6
    r = client.post("/todos", json={"title": char * 201})
    assert_error(r, 422, "title_too_long", "Title must be at most 200 characters")
    assert client.get("/todos").json() == []


def test_create_title_too_long_after_trim_boundary(client: TestClient):  # AC-001.6
    r = client.post("/todos", json={"title": " " + "a" * 201 + " "})
    assert_error(r, 422, "title_too_long", "Title must be at most 200 characters")
    assert client.get("/todos").json() == []


@pytest.mark.parametrize("title", ["a" * 200, "é" * 200, "  " + "a" * 200 + "  "])
def test_create_title_exactly_200(client: TestClient, title: str):  # AC-001.7
    r = client.post("/todos", json={"title": title})
    assert r.status_code == 201, r.text
    assert len(r.json()["title"]) == 200
    assert len(client.get("/todos").json()[0]["title"]) == 200


@pytest.mark.parametrize(
    "raw",
    [b"{not json", b"", b"[]", b'"x"', b"42", b'{"title": 42}', b'{"title": true}', b'{"title": ["x"]}'],
)
def test_create_invalid_request(client: TestClient, raw: bytes):  # AC-001.8
    r = post_raw(client, raw)
    assert_error(r, 422, "invalid_request")
    assert client.get("/todos").json() == []


def test_create_ignores_other_fields(client: TestClient):  # AC-001.8
    r = client.post(
        "/todos",
        json={"title": "x", "done": True, "id": "nope", "created_at": "2000-01-01", "extra": 1},
    )
    assert r.status_code == 201
    body = r.json()
    assert body["done"] is False
    assert body["id"] != "nope"
    assert body["created_at"] != "2000-01-01"


# ---------------------------------------------------------------- AC-001.9 / .10 / .11


def test_patch_mark_done(client: TestClient):  # AC-001.9
    todo = create(client)
    r = client.patch(f"/todos/{todo['id']}", json={"done": True})
    assert r.status_code == 200
    assert r.json() == {**todo, "done": True}
    assert client.get("/todos").json() == [{**todo, "done": True}]
    again = client.patch(f"/todos/{todo['id']}", json={"done": True})
    assert again.status_code == 200
    assert again.json()["done"] is True


def test_patch_mark_not_done(client: TestClient):  # AC-001.10
    todo = create(client)
    client.patch(f"/todos/{todo['id']}", json={"done": True})
    r = client.patch(f"/todos/{todo['id']}", json={"done": False})
    assert r.status_code == 200
    assert r.json() == todo
    assert client.get("/todos").json() == [todo]
    again = client.patch(f"/todos/{todo['id']}", json={"done": False})
    assert again.status_code == 200
    assert again.json()["done"] is False


@pytest.mark.parametrize(
    "raw", [b"[]", b'"x"', b"{not json", b"", b"{}", b'{"done": "true"}', b'{"done": 1}', b'{"done": null}']
)
def test_patch_invalid_request(client: TestClient, raw: bytes):  # AC-001.11
    todo = create(client)
    r = patch_raw(client, todo["id"], raw)
    assert_error(r, 422, "invalid_request")
    assert client.get("/todos").json() == [todo]


# ---------------------------------------------------------------- AC-001.12 / .13 / .14


def test_delete_removes_only_that_todo(client: TestClient):  # AC-001.12
    a, b, c = (create(client, t) for t in "abc")
    r = client.delete(f"/todos/{b['id']}")
    assert r.status_code == 204
    assert r.content == b""
    assert client.get("/todos").json() == [a, c]


def test_unknown_id_is_404_without_side_effects(client: TestClient):  # AC-001.13
    keep = create(client)
    gone = create(client, "gone")
    assert client.delete(f"/todos/{gone['id']}").status_code == 204
    for tid in (str(uuid.uuid4()), gone["id"], "abc"):
        assert_error(
            client.patch(f"/todos/{tid}", json={"done": True}),
            404, "todo_not_found", "This todo no longer exists",
        )
        assert_error(
            client.delete(f"/todos/{tid}"), 404, "todo_not_found", "This todo no longer exists"
        )
    assert client.get("/todos").json() == [keep]


def test_shared_list_without_credentials(client: TestClient, postgres_url: str):  # AC-001.14
    todo = create(client)
    other = TestClient(make_app(postgres_url))
    with other:
        r = other.get("/todos", headers={"X-Anything": "1", "Cookie": "a=b"})
        assert r.status_code == 200
        assert r.json() == [todo]
        assert other.get("/todos").json() == [todo]
    for resp in (client.get("/todos"), client.post("/todos", json={"title": "x"})):
        assert resp.status_code != 401 and resp.status_code != 403


# ---------------------------------------------------------------- AC-001.15 / .16


def test_fresh_database_starts_and_keeps_todos(postgres_url: str, no_db):  # AC-001.15
    drop_todos(postgres_url)
    with running(postgres_url) as c:
        assert c.get("/ready").json() == {"status": "ready"}
        r = c.get("/todos")
        assert r.status_code == 200
        assert r.json() == []
        todo = create(c)
    with running(postgres_url) as c:
        assert c.get("/todos").json() == [todo]


def test_restart_keeps_todos_ids_and_order(postgres_url: str, no_db):  # AC-001.16
    drop_todos(postgres_url)
    with running(postgres_url) as c:
        a, b, d = (create(c, t) for t in ("a", "b", "c"))
        c.patch(f"/todos/{b['id']}", json={"done": True})
        before = c.get("/todos").json()
    assert [t["done"] for t in before] == [False, True, False]
    with running(postgres_url) as c:
        assert c.get("/todos").json() == before


# ---------------------------------------------------------------- AC-001.17 / .18


def _assert_unreachable(c: TestClient) -> None:
    some_id = str(uuid.uuid4())
    calls = [
        lambda: c.get("/todos"),
        lambda: c.post("/todos", json={"title": "x"}),
        lambda: c.patch(f"/todos/{some_id}", json={"done": True}),
        lambda: c.delete(f"/todos/{some_id}"),
    ]
    for call in calls:
        start = time.monotonic()
        r = call()
        assert time.monotonic() - start < 3
        assert r.status_code == 503, r.text
        assert r.json() == UNAVAILABLE
    start = time.monotonic()
    ready = c.get("/ready")
    assert time.monotonic() - start < 3
    assert ready.status_code == 503
    health = c.get("/health")
    assert health.status_code == 200
    assert health.json() == {"status": "ok"}


def test_unreachable_database_refused(no_db):  # AC-001.17
    with TestClient(make_app(UNREACHABLE_URL)) as c:
        _assert_unreachable(c)


def test_unreachable_database_hanging(container_url):  # AC-001.17
    container = make_container_started(container_url)
    url = container.get_connection_url()
    with TestClient(make_app(url)) as c:
        assert c.get("/todos").status_code == 200
        container.get_wrapped_container().pause()
        try:
            _assert_unreachable(c)
        finally:
            container.get_wrapped_container().unpause()


def make_container_started(start):
    return start()


def test_recovery_without_restart(container_url):  # AC-001.18
    container = make_container_started(container_url)
    url = container.get_connection_url()
    with TestClient(make_app(url)) as c:
        todo = create(c)
        container.get_wrapped_container().pause()
        assert c.get("/ready").status_code == 503
        assert c.get("/todos").status_code == 503
        container.get_wrapped_container().unpause()
        deadline = time.monotonic() + 15
        ready = c.get("/ready")
        while ready.status_code != 200 and time.monotonic() < deadline:
            time.sleep(0.5)
            ready = c.get("/ready")
        assert ready.status_code == 200
        assert ready.json() == {"status": "ready"}
        r = c.get("/todos")
        assert r.status_code == 200
        assert r.json() == [todo]
