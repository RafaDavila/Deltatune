from fastapi import FastAPI
from fastapi.middleware.cors import (
    CORSMiddleware,
)

from app.config import settings
from app.routers.challenges import (
    router as challenges_router,
)
from app.routers.songs import (
    router as songs_router,
)
from app.routers.infinite_games import (
    router as infinite_games_router,
)


app = FastAPI(
    title="Deltatune API",
    description=(
        "API responsável pelos desafios "
        "diários de Deltatune"
    ),
    version="0.1.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(challenges_router)
app.include_router(songs_router)
app.include_router(infinite_games_router)


@app.get("/health", tags=["Health"])
def health_check() -> dict[str, str]:
    return {"status": "ok"}