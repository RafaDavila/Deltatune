from fastapi import FastAPI

app = FastAPI (
    title="Deltatune API",
    description="Api responsável pelos desafios diários de Deltatune",
    version="0.1.0",
)

@app.get("/health", tags=["Health"])
def health_check() -> dict[str, str]:
    return{"status":"ok"}