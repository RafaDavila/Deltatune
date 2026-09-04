from typing import Any

from pytest import MonkeyPatch

from app.config import settings
from app.services.email_service import (
    BREVO_EMAIL_API_URL,
    send_password_reset_email,
)


class FakeResponse:
    def raise_for_status(self) -> None:
        pass


def test_send_password_reset_email(
    monkeypatch: MonkeyPatch,
) -> None:
    captured_request: dict[str, Any] = {}

    def fake_post(
        url: str,
        **kwargs: Any,
    ) -> FakeResponse:
        captured_request["url"] = url
        captured_request.update(kwargs)

        return FakeResponse()

    monkeypatch.setattr(
        "app.services.email_service.httpx2.post",
        fake_post,
    )

    send_password_reset_email(
        recipient_email="usuario@example.com",
        reset_token="token-seguro",
    )

    assert (
        captured_request["url"]
        == BREVO_EMAIL_API_URL
    )

    payload = captured_request["json"]

    assert payload["sender"] == {
        "name": "Deltatune",
        "email": str(
            settings.email_from_address,
        ),
    }

    assert payload["to"] == [
        {
            "email": "usuario@example.com",
        }
    ]

    assert (
        "token-seguro"
        in payload["htmlContent"]
    )

    assert (
        settings.frontend_reset_password_url
        in payload["textContent"]
    )