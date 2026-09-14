from ipaddress import (
    IPv6Address,
    ip_address,
)

from fastapi import (
    HTTPException,
    Request,
    status,
)

from app.config import settings


def normalize_client_ip(
    value: str,
) -> str:
    address = ip_address(value.strip())

    if (
        isinstance(address, IPv6Address)
        and address.ipv4_mapped is not None
    ):
        return str(address.ipv4_mapped)

    return str(address)

def get_client_ip(
    request: Request,
) -> str:
    if settings.trust_cloudflare_client_ip:
        values = request.headers.getlist(
            "cf-connecting-ip",
        )

        raw_ip = (
            values[0]
            if len(values) == 1
            else None
        )
    else:
        raw_ip = (
            request.client.host
            if request.client is not None
            else None
        )

    if raw_ip is not None:
        try:
            return normalize_client_ip(raw_ip)
        except ValueError:
            pass

    raise HTTPException(
        status_code=(
            status.HTTP_503_SERVICE_UNAVAILABLE
        ),
        detail=(
            "Não foi possível processar "
            "a solicitação. Tente novamente."
        ),
    )