#!/bin/bash
# ─────────────────────────────────────────────────────────────
# Core Cloud Server – Network Emulation Startup
# Adds 40 ms delay (±5 ms jitter) to simulate a remote data centre
# ─────────────────────────────────────────────────────────────

echo "[CLOUD] Applying 40ms netem delay on eth0 ..."
tc qdisc add dev eth0 root netem delay 40ms 5ms distribution normal 2>/dev/null || \
tc qdisc change dev eth0 root netem delay 40ms 5ms distribution normal
echo "[CLOUD] Network latency configured: 40ms ± 5ms"

echo "[CLOUD] Starting Flask server on port 5002 ..."
exec python app.py
