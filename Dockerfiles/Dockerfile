FROM python:3.12-alpine AS builder

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /build

# Install build dependencies
RUN apk add --no-cache \
    build-base \
    postgresql-dev \
    libffi-dev \
    openssl-dev

# Install uv (only binary)
COPY --from=ghcr.io/astral-sh/uv:0.10.0 /uv /uvx /bin/

# Copy dependency metadata
COPY pyproject.toml uv.lock ./

# Export locked dependencies
RUN uv export > requirements.txt
# Install directly into system Python
RUN uv pip install --system --no-cache \
    -r requirements.txt && \
    rm -f /bin/uv /bin/uvx requirements.txt

FROM builder AS appbuild

WORKDIR /app
COPY . .

RUN python manage.py collectstatic --noinput 

FROM python:3.12-alpine AS runtime

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Runtime libs only
RUN apk add --no-cache \
    libpq \
    tini \
    curl

# Copy installed Python site-packages and binaries
COPY --from=builder /usr/local /usr/local

# Copy application
COPY --from=appbuild /app /app

ENTRYPOINT ["/sbin/tini", "--"]

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]