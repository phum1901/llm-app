FROM python:3.12-slim

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV PATH="/app/.venv/bin:$PATH"

ENV PYTHONPATH=/app

COPY ./pyproject.toml ./uv.lock /app/

RUN uv sync --frozen

COPY ./app /app/app
