from fastapi import FastAPI
from app.routers.challenges import router as challenges_router
from fastapi.middleware.cors import CORSMiddleware
from app.routers.songs import router as songs_router

app = FastAPI (
    title="Deltatune API",
    description="Api responsável pelos desafios diários de Deltatune",
    version="0.1.0",
)

allowed_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(challenges_router)

@app.get("/health", tags=["Health"])
def health_check() -> dict[str, str]:
    return{"status":"ok"}

app.include_router(challenges_router)
app.include_router(songs_router)