# ------------------------------------------------------------
# 🐍 Stage 1 : Build des dépendances
# ------------------------------------------------------------
FROM python:3.11-slim AS builder

WORKDIR /app

# Optimisation Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Dépendances système nécessaires (argon2 + psycopg2)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libffi-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copie du requirements
COPY requirements.txt .

# Construction d’un venv PRODUCTION
RUN python -m venv /venv && \
    /venv/bin/pip install --no-cache-dir -r requirements.txt


# ------------------------------------------------------------
# 🚀 Stage 2 : Image finale ultra légère
# ------------------------------------------------------------
FROM python:3.11-slim

WORKDIR /app

# Optimisation Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Copie du venv buildé
COPY --from=builder /venv /venv

# Active le venv dans PATH
ENV PATH="/venv/bin:$PATH"

# Copier uniquement le code utile
COPY app ./app

# Serveur Gunicorn + UvicornWorker (PROD)
CMD ["gunicorn", "app.main:app", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000", "--workers", "4"]
