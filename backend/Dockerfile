# COPIE API · build context = backend/ · data/ is mounted at /app/data by docker-compose.yml
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Modules find data/ at <repo>/data, so the code lives in /app/backend and data in /app/data
WORKDIR /app/backend

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
