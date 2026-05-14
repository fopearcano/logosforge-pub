FROM python:3.12-slim

# Match the slim image's runtime needs for both SQLite (built in) and
# PostgreSQL (libpq).
RUN apt-get update \
    && apt-get install -y --no-install-recommends libpq5 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install dependencies (Postgres driver included so the same image can
# serve either backend).
COPY requirements.txt requirements-postgres.txt ./
RUN pip install --no-cache-dir -r requirements-postgres.txt

COPY app ./app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    LOG_LEVEL=INFO

# Storage root for uploaded attachments. Mount a volume here in
# production so files survive container restarts.
VOLUME ["/app/storage"]

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
