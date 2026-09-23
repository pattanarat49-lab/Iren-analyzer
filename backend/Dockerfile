# IREN Analyzer backend (FastAPI). Build from the backend/ directory:
#   docker build -t iren-backend backend
FROM python:3.11-slim

# LightGBM needs the OpenMP runtime.
RUN apt-get update \
    && apt-get install -y --no-install-recommends libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app/backend
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Everything that must survive restarts (SQLite DB + trained models) lives in /app/var:
# mount a persistent volume there.
ENV PYTHONUNBUFFERED=1 \
    DATABASE_URL=sqlite:////app/var/iren.db \
    MODELS_DIR=/app/var/models
RUN mkdir -p /app/var
VOLUME ["/app/var"]

EXPOSE 8000
# Single worker on purpose: the live market hub, scheduler and WebSocket clients live in memory.
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1"]
