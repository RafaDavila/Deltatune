import pytest

from app.services.client_ip import (
    normalize_client_ip,
)

from fastapi import HTTPException, Request

from app.config import settings
from app.services.client_ip import get_client_ip


@pytest.mark.parametrize(
    ("original", "expected"),
    [
        ("192.0.2.1", "192.0.2.1"),
        ("::ffff:192.0.2.1", "192.0.2.1"),
        (
            "2001:0db8:0000:0000:0000:0000:0000:0001",
            "2001:db8::1",
        ),
    ],
)
def test_normalizes_client_ip(
    original: str,
    expected: str,
) -> None:
    assert normalize_client_ip(original) == expected


@pytest.mark.parametrize(
    "value",
    [
        "nao-e-um-ip",
        "192.0.2.1, 198.51.100.1",
    ],
)
def test_rejects_invalid_client_ip(
    value: str,
) -> None:
    with pytest.raises(ValueError):
        normalize_client_ip(value)


def make_request(
    headers: list[tuple[bytes, bytes]],
    client_host: str | None = "192.0.2.10",
) -> Request:
    return Request(
        {
            "type": "http",
            "headers": headers,
            "client": (
                (client_host, 12345)
                if client_host is not None
                else None
            ),
        },
    )


def test_ignores_headers_when_proxy_is_not_trusted(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        settings,
        "trust_cloudflare_client_ip",
        False,
    )

    request = make_request(
        headers=[
            (b"cf-connecting-ip", b"198.51.100.1"),
            (b"x-forwarded-for", b"198.51.100.2"),
        ],
    )

    assert get_client_ip(request) == "192.0.2.10"


def test_reads_ip_from_trusted_proxy(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        settings,
        "trust_cloudflare_client_ip",
        True,
    )

    request = make_request(
        headers=[
            (
                b"cf-connecting-ip",
                b"::ffff:198.51.100.1",
            ),
        ],
    )

    assert get_client_ip(request) == "198.51.100.1"


@pytest.mark.parametrize(
    "headers",
    [
        [],
        [(b"cf-connecting-ip", b"invalido")],
        [
            (
                b"cf-connecting-ip",
                b"192.0.2.1, 198.51.100.1",
            ),
        ],
        [
            (b"cf-connecting-ip", b"192.0.2.1"),
            (b"cf-connecting-ip", b"198.51.100.1"),
        ],
    ],
)
def test_rejects_unusable_proxy_header(
    monkeypatch: pytest.MonkeyPatch,
    headers: list[tuple[bytes, bytes]],
) -> None:
    monkeypatch.setattr(
        settings,
        "trust_cloudflare_client_ip",
        True,
    )

    request = make_request(headers=headers)

    with pytest.raises(HTTPException) as error:
        get_client_ip(request)

    assert error.value.status_code == 503


@pytest.mark.parametrize(
    "client_host",
    [None, "invalido"],
)
def test_rejects_unusable_connection_ip(
    monkeypatch: pytest.MonkeyPatch,
    client_host: str | None,
) -> None:
    monkeypatch.setattr(
        settings,
        "trust_cloudflare_client_ip",
        False,
    )

    request = make_request(
        headers=[],
        client_host=client_host,
    )

    with pytest.raises(HTTPException) as error:
        get_client_ip(request)

    assert error.value.status_code == 503