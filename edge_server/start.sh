#!/bin/bash
# ─────────────────────────────────────────────────────────────
# MEC Edge Server – Network Emulation Startup
# Adds 5 ms delay  (±1 ms jitter) to simulate a 5G cell tower
# ─────────────────────────────────────────────────────────────

echo "[EDGE] Applying 5ms netem delay on eth0 ..."
tc qdisc add dev eth0 root netem delay 5ms 1ms distribution normal 2>/dev/null || \
tc qdisc change dev eth0 root netem delay 5ms 1ms distribution normal
echo "[EDGE] Network latency configured: 5ms ± 1ms"

echo "[EDGE] Starting Flask server on port 5001 ..."
exec python app.py
