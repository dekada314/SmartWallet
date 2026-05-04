FROM python:3.14-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /SmartWallet

ENV PYTHONUNBUFFERED=1 \ 
    PYTHONDONTWRITEBYTECODE=1

COPY pyproject.toml uv.lock .python-version /SmartWallet/

RUN uv sync --frozen --no-cache

COPY . .

CMD uv run python3 -m app.main