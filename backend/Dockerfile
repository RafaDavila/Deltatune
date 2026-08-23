FROM python:3.14-slim-bookworm

ENV PYTHONDONTWRITEBYCODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip \ && pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["sh", "-c", "alembic upgrade head && python -m scripts.seed_songs && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]