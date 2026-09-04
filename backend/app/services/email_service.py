from html import escape
from urllib.parse import urlencode

import httpx2

from app.config import settings


BREVO_EMAIL_API_URL = (
    "https://api.brevo.com/v3/smtp/email"
)


class EmailDeliveryError(RuntimeError):
    pass


def build_password_reset_url(
    reset_token: str,
) -> str:
    query = urlencode({
        "token": reset_token,
    })

    return (
        f"{settings.frontend_reset_password_url}"
        f"?{query}"
    )


def send_password_reset_email(
    recipient_email: str,
    reset_token: str,
) -> None:
    reset_url = build_password_reset_url(
        reset_token,
    )

    safe_reset_url = escape(
        reset_url,
        quote=True,
    )

    payload = {
        "sender": {
            "name": "Deltatune",
            "email": str(
                settings.email_from_address,
            ),
        },
        "to": [
            {
                "email": recipient_email,
            },
        ],
        "subject": (
            "Redefinição de senha do Deltatune"
        ),
        "htmlContent": (
            "<h1>Redefinição de senha</h1>"
            "<p>Recebemos uma solicitação para "
            "redefinir sua senha no Deltatune.</p>"
            f'<p><a href="{safe_reset_url}">'
            "Redefinir minha senha"
            "</a></p>"
            "<p>Esse link expira em "
            f"{settings.password_reset_token_expire_minutes} "
            "minutos.</p>"
            "<p>Se você não fez essa solicitação, "
            "ignore este e-mail.</p>"
        ),
        "textContent": (
            "Recebemos uma solicitação para redefinir "
            "sua senha no Deltatune.\n\n"
            f"Acesse: {reset_url}\n\n"
            "Esse link expira em "
            f"{settings.password_reset_token_expire_minutes} "
            "minutos.\n\n"
            "Se você não fez essa solicitação, "
            "ignore este e-mail."
        ),
    }

    try:
        response = httpx2.post(
            BREVO_EMAIL_API_URL,
            headers={
                "accept": "application/json",
                "api-key": (
                    settings.brevo_api_key
                    .get_secret_value()
                ),
                "content-type": "application/json",
            },
            json=payload,
            timeout=10.0,
        )

        response.raise_for_status()
    except httpx2.HTTPError as error:
        raise EmailDeliveryError(
            "Não foi possível enviar o e-mail.",
        ) from error