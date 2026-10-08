"""Acceptance tests for spec 002: change a todo's title through PATCH /todos/{id}."""

from __future__ import annotations

import time
import uuid

import pytest
from conftest import make_app, running
from fastapi.testclient import TestClient

REQUIRED = ("title_required", "Title is required")
TOO_LONG = ("title_too_long", "Title must be at most 200 characters")
NOT_FOUND = ("todo_not_found", "This todo no longer exists")
UNAVAILABLE = ("unavailable", "Todos are unavailable, please try again")
FIELDS = {"id", "title", "done", "created_at"}


def assert_error(resp, status: int, err: tuple[str, str] | str, message: str | None = None) -> None:
    code, msg = (err, message) if isinstance(err, str) else err
    assert resp.status_code == status, resp.text
    assert resp.headers["content-type"].startswith("application/json")
    body = resp.json()
    assert set(body) == {"error"}
    assert set(body["error"]) == {"code", "message"}
    assert body["error"]["code"] == code
    if msg is None:
        assert body["error"]["message"]
    else:
        assert body["error"]["message"] == msg


def create(client: TestClient, title: str = "Buy milk") -> dict:
    r = client.post("/todos", json={"title": title})
    assert r.status_code == 201, r.text
    return r.json()


def patch_raw(client: TestClient, todo_id: str, raw: bytes):
    return client.patch(
        f"/todos/{todo_id}", content=raw, headers={"Content-Type": "application/json"}
    )


def patch_title(client: TestClient, todo_id: str, title):
    return client.patch(f"/todos/{todo_id}", json={"title": title})


def test_title_change_persists_across_restart(client: TestClient, postgres_url: str):  # AC-002.1
    todo = create(client)
    r = patch_title(client, todo["id"], "Buy oat milk")
    assert r.status_code == 200, r.text
    assert r.json() == {**todo, "title": "Buy oat milk"}
    assert set(r.json()) == FIELDS
    assert client.get("/todos").json() == [{**todo, "title": "Buy oat milk"}]
    with running(postgres_url) as c2:
        assert c2.get("/todos").json() == [{**todo, "title": "Buy oat milk"}]


def test_title_change_keeps_order_and_done(client: TestClient):  # AC-002.2
    a, b, c = (create(client, t) for t in ("a", "b", "c"))
    assert client.patch(f"/todos/{b['id']}", json={"done": True}).status_code == 200
    before = client.get("/todos").json()
    assert [t["done"] for t in before] == [False, True, False]
    r = patch_title(client, b["id"], "b changed")
    assert r.status_code == 200, r.text
    after = client.get("/todos").json()
    assert [t["id"] for t in after] == [a["id"], b["id"], c["id"]]
    assert after[1] == {**before[1], "title": "b changed"}
    assert after[1]["done"] is True
    assert after[0] == before[0]
    assert after[2] == before[2]


def test_title_and_done_together_and_same_title(client: TestClient):  # AC-002.3
    todo = create(client)
    r = client.patch(f"/todos/{todo['id']}", json={"title": "Buy oat milk", "done": True})
    assert r.status_code == 200, r.text
    assert r.json() == {**todo, "title": "Buy oat milk", "done": True}
    assert client.get("/todos").json() == [r.json()]
    same = patch_title(client, todo["id"], "Buy oat milk")
    assert same.status_code == 200, same.text
    assert same.json() == {**todo, "title": "Buy oat milk", "done": True}
    assert client.get("/todos").json() == [same.json()]


def test_title_is_trimmed_inner_spaces_kept(client: TestClient):  # AC-002.4
    todo = create(client)
    r = patch_title(client, todo["id"], "  Buy oat milk\t\n")
    assert r.status_code == 200, r.text
    assert r.json()["title"] == "Buy oat milk"
    assert client.get("/todos").json()[0]["title"] == "Buy oat milk"
    r = patch_title(client, todo["id"], "Buy  oat milk")
    assert r.status_code == 200, r.text
    assert r.json()["title"] == "Buy  oat milk"
    assert client.get("/todos").json()[0]["title"] == "Buy  oat milk"


@pytest.mark.parametrize(
    "body",
    [
        {"title": None},
        {"title": ""},
        {"title": "   "},
        {"title": "  ", "done": True},
        {"title": None, "done": True},
    ],
)
def test_title_required(client: TestClient, body: dict):  # AC-002.5
    todo = create(client)
    r = client.patch(f"/todos/{todo['id']}", json=body)
    assert_error(r, 422, REQUIRED)
    assert client.get("/todos").json() == [todo]


@pytest.mark.parametrize("char", ["a", "é"])
@pytest.mark.parametrize("with_done", [False, True])
def test_title_too_long(client: TestClient, char: str, with_done: bool):  # AC-002.6
    todo = create(client)
    body = {"title": char * 201}
    if with_done:
        body["done"] = True
    r = client.patch(f"/todos/{todo['id']}", json=body)
    assert_error(r, 422, TOO_LONG)
    assert client.get("/todos").json() == [todo]


def test_title_too_long_after_trim_boundary(client: TestClient):  # AC-002.6
    todo = create(client)
    r = patch_title(client, todo["id"], " " + "a" * 201 + " ")
    assert_error(r, 422, TOO_LONG)
    assert client.get("/todos").json() == [todo]


@pytest.mark.parametrize("title", ["a" * 200, "é" * 200, " " + "a" * 200 + " "])
def test_title_exactly_200(client: TestClient, title: str):  # AC-002.7
    todo = create(client)
    r = patch_title(client, todo["id"], title)
    assert r.status_code == 200, r.text
    assert len(r.json()["title"]) == 200
    assert len(client.get("/todos").json()[0]["title"]) == 200


@pytest.mark.parametrize("value", [42, True, ["x"], {}])
def test_title_not_a_string(client: TestClient, value):  # AC-002.8
    todo = create(client)
    r = patch_title(client, todo["id"], value)
    assert_error(r, 422, "invalid_request")
    assert client.get("/todos").json() == [todo]


def test_unknown_ids_are_404_without_side_effects(client: TestClient):  # AC-002.9
    todo = create(client)
    gone = create(client, "gone")
    assert client.delete(f"/todos/{gone['id']}").status_code == 204
    for tid in (str(uuid.uuid4()), gone["id"], "abc"):
        r = patch_title(client, tid, "Buy oat milk")
        assert_error(r, 404, NOT_FOUND)
    assert client.get("/todos").json() == [todo]


@pytest.mark.parametrize(
    ("raw", "status", "err"),
    [
        (b"[]", 422, "invalid_request"),
        (b"{not json", 422, "invalid_request"),
        (b"{}", 422, "invalid_request"),
        (b'{"foo": 1}', 422, "invalid_request"),
        (b'{"done": "x", "title": null}', 422, "invalid_request"),
        (b'{"done": null, "title": "ok"}', 422, "invalid_request"),
        (b'{"title": null, "done": true}', 422, REQUIRED),
        (b'{"title": 42, "done": true}', 422, "invalid_request"),
        (b'{"title": "   "}', 422, REQUIRED),
        (b'{"title": "' + b"a" * 201 + b'"}', 422, TOO_LONG),
    ],
)
@pytest.mark.parametrize("target", ["unknown", "deleted", "abc"])
def test_rule_order_before_id_lookup(client: TestClient, raw, status, err, target):  # AC-002.10
    gone = create(client, "gone")
    client.delete(f"/todos/{gone['id']}")
    tid = {"unknown": str(uuid.uuid4()), "deleted": gone["id"], "abc": "abc"}[target]
    assert_error(patch_raw(client, tid, raw), status, err)


def test_rule_order_on_existing_todo(client: TestClient):  # AC-002.10
    todo = create(client)
    assert_error(patch_raw(client, todo["id"], b'{"done": "x", "title": null}'), 422, "invalid_request")
    assert_error(patch_raw(client, todo["id"], b'{"title": null, "done": true}'), 422, REQUIRED)
    assert client.get("/todos").json() == [todo]


@pytest.mark.parametrize(
    "body", [{"done": True}, {"done": True, "foo": 1}, {"done": True, "id": "x", "updated_at": 1}]
)
def test_done_only_unchanged_title(client: TestClient, body: dict):  # AC-002.11
    todo = create(client)
    r = client.patch(f"/todos/{todo['id']}", json=body)
    assert r.status_code == 200, r.text
    assert r.json() == {**todo, "done": True}
    assert client.get("/todos").json() == [{**todo, "done": True}]
    back = client.patch(f"/todos/{todo['id']}", json={"done": False, "extra": [1]})
    assert back.status_code == 200
    assert back.json() == todo
    assert_error(client.patch(f"/todos/{uuid.uuid4()}", json=body), 404, NOT_FOUND)
    assert_error(client.patch("/todos/abc", json=body), 404, NOT_FOUND)


def test_last_write_wins_no_conflict(client: TestClient):  # AC-002.12
    todo = create(client)
    assert patch_title(client, todo["id"], "A").status_code == 200
    r = client.patch(
        f"/todos/{todo['id']}", json={"title": "B"}, headers={"If-Match": '"stale"'}
    )
    assert r.status_code == 200, r.text
    assert r.json()["title"] == "B"
    assert client.get("/todos").json()[0]["title"] == "B"


def test_title_patch_keeps_other_callers_done(client: TestClient, postgres_url: str):  # AC-002.12
    todo = create(client)
    with running(postgres_url) as other:
        assert other.patch(f"/todos/{todo['id']}", json={"done": True}).status_code == 200
    r = patch_title(client, todo["id"], "Renamed")
    assert r.status_code == 200, r.text
    assert r.json()["done"] is True
    assert client.get("/todos").json()[0]["done"] is True


def test_unreachable_database_title_patch(container_url):  # AC-002.13
    container = container_url()
    url = container.get_connection_url()
    with TestClient(make_app(url)) as c:
        todo = create(c)
        container.get_wrapped_container().pause()
        try:
            start = time.monotonic()
            r = patch_title(c, todo["id"], "Buy oat milk")
            assert time.monotonic() - start < 3
            assert_error(r, 503, UNAVAILABLE)
        finally:
            container.get_wrapped_container().unpause()
        deadline = time.monotonic() + 15
        ready = c.get("/ready")
        while ready.status_code != 200 and time.monotonic() < deadline:
            time.sleep(0.5)
            ready = c.get("/ready")
        assert ready.status_code == 200
        assert c.get("/todos").json() == [todo]
