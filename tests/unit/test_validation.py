import pytest

from todo_api.errors import ApiError
from todo_api.todos.validation import parse_create, parse_id, parse_patch


@pytest.mark.parametrize(
    ("raw", "code"),
    [
        (b"nope", "invalid_request"),
        (b"[]", "invalid_request"),
        (b'"x"', "invalid_request"),
        (b"{}", "title_required"),
        (b'{"title": null}', "title_required"),
        (b'{"title": 42}', "invalid_request"),
        (b'{"title": true}', "invalid_request"),
        (b'{"title": ["x"]}', "invalid_request"),
        (b'{"title": ""}', "title_required"),
        (b'{"title": "   "}', "title_required"),
        (('{"title": "' + "a" * 201 + '"}').encode(), "title_too_long"),
        (('{"title": "' + "é" * 201 + '"}').encode(), "title_too_long"),
    ],
)
def test_parse_create_rejects(raw: bytes, code: str) -> None:
    with pytest.raises(ApiError) as exc:
        parse_create(raw)
    assert exc.value.status == 422
    assert exc.value.code == code


def test_parse_create_accepts_and_strips() -> None:
    assert parse_create(b'{"title": "  hi  ", "done": true}') == "hi"
    assert parse_create(('{"title": " ' + "a" * 200 + ' "}').encode()) == "a" * 200


@pytest.mark.parametrize(
    "raw", [b"x", b"[]", b"{}", b'{"done": "true"}', b'{"done": 1}', b'{"done": null}']
)
def test_parse_patch_rejects(raw: bytes) -> None:
    with pytest.raises(ApiError) as exc:
        parse_patch(raw)
    assert exc.value.code == "invalid_request"


def test_parse_patch_accepts() -> None:
    assert parse_patch(b'{"done": true}') is True
    assert parse_patch(b'{"done": false}') is False


def test_parse_id() -> None:
    assert parse_id("abc") is None
    assert parse_id("12345678-1234-5678-1234-567812345678") is not None
