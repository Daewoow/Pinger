ARG PYTHON_VERSION=3.12.1
FROM python:${PYTHON_VERSION}-alpine
LABEL authors="Lorem Ipsum"

ENV PYTHONPATH=/app

ENV UV_SYSTEM_PYTHON=1

ENV UV_PROJECT_ENVIRONMENT=/usr/local

WORKDIR /app

COPY uv.lock .
COPY pyproject.toml .

RUN apk add --no-cache \
    mesa-gl \
    glib \
    libsm \
    libxext \
    libxrender

RUN pip install uv && uv sync \
  --no-dev \
  --no-install-project \
  --frozen

COPY . .

EXPOSE 5123

CMD alembic upgrade head && uvicorn 'app.main:app' --host=0.0.0.0 --port=5123 --reload