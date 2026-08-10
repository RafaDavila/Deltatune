from fastapi import FastAPI
from app.routers.challenges import router as challenges_router

app = FastAPI (
    title="Deltatune API",
    description="Api responsável pelos desafios diários de Deltatune",
    version="0.1.0",
)

app.include_router(challenges_router)

@app.get("/health", tags=["Health"])
def health_check() -> dict[str, str]:
    return{"status":"ok"}