from typing import Annotated

from fastapi import Header


GuestGameToken = Annotated[
    str | None,
    Header(
        alias="X-Guest-Token",
        max_length=128,
    ),
]