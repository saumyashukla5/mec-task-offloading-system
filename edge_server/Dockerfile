# ── Edge Server Dockerfile ──────────────────────────────────
FROM python:3.11-slim

# iproute2 provides the 'tc' command for network emulation
RUN apt-get update && \
    apt-get install -y --no-install-recommends iproute2 && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
COPY start.sh .
RUN chmod +x start.sh

EXPOSE 5001

ENV PORT=5001

CMD ["./start.sh"]
