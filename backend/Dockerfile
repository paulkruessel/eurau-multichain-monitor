FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Dependency-Metadaten
COPY pyproject.toml uv.lock README.md ./

# Dependencies installieren, Projekt selbst noch nicht
RUN uv sync --frozen --no-cache --no-dev --no-install-project

# Source Code
COPY src ./src

# Jetzt das eigene Projekt installieren
RUN uv sync --frozen --no-cache --no-dev

EXPOSE 8000

CMD ["/app/.venv/bin/uvicorn", "backend.main:app", \
     "--host", "0.0.0.0", \
     "--port", "8000", \
     "--app-dir", "/app/src"]