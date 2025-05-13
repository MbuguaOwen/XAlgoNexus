FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH="/app/src"

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev curl \
 && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy from root context since build context is ../
COPY requirements.txt .
COPY wheels-linux/ /wheels/

RUN pip install --timeout=60 --retries=10 \
    --no-cache-dir --find-links=/wheels --no-index \
    -r requirements.txt

COPY src/ /app/src/
COPY config/ /app/config/
COPY infra/monitoring/ /app/monitoring/
COPY ml_model/ /app/ml_model/
COPY entrypoint.sh /app/entrypoint.sh

RUN chmod +x /app/entrypoint.sh

EXPOSE 9100
HEALTHCHECK --interval=15s --timeout=3s --start-period=20s --retries=3 \
  CMD curl --fail http://localhost:9100/metrics || exit 1

CMD ["./entrypoint.sh"]
