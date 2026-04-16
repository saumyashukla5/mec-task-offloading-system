# MEC Emulation Project – Complete Guide (Windows)

## What This Project Does
Emulates a **Multi-Access Edge Computing (MEC)** environment using Docker.
Two virtual servers are spun up:

| Server | Port | Simulated Latency | Task Type |
|--------|------|--------------------|-----------|
| MEC Edge Host | 5001 | 5 ms (5G cell tower) | URLLC |
| Core Cloud | 5002 | 40 ms (remote data centre) | eMBB |

The orchestrator generates random tasks, routes them intelligently,
measures the **actual Round-Trip Time (RTT)**, logs it to CSV, and
draws 4 publication-quality graphs.

---

## Prerequisites (Install These First)

1. **Docker Desktop for Windows**
   https://www.docker.com/products/docker-desktop/
   → During install, select **"Use WSL 2"** (recommended)

2. **Python 3.10+**
   https://www.python.org/downloads/
   → During install, tick **"Add Python to PATH"**

---

## Folder Structure

```
mec_emulation/
├── edge_server/
│   ├── app.py          ← Flask server (Edge)
│   ├── start.sh        ← Adds 5ms tc netem delay
│   ├── requirements.txt
│   └── Dockerfile
├── cloud_server/
│   ├── app.py          ← Flask server (Cloud)
│   ├── start.sh        ← Adds 40ms tc netem delay
│   ├── requirements.txt
│   └── Dockerfile
├── client_orchestrator/
│   ├── orchestrator.py ← The UE client + graphs
│   └── requirements.txt
├── results/            ← CSV + PNG graphs saved here
├── docker-compose.yml
├── RUN_PROJECT.bat     ← ★ Double-click to run everything
└── STOP_PROJECT.bat    ← Double-click to stop containers
```

---

## How to Run

### Option A – Easiest (One Click)
1. Open Docker Desktop and wait for it to start (whale icon in taskbar).
2. Double-click **`RUN_PROJECT.bat`**.
3. Watch the terminal – it will build, start, simulate, and open results.

### Option B – Manual (Step by Step)

Open **Command Prompt** in the `mec_emulation\` folder:

```cmd
REM Step 1 – Build and start servers
docker-compose up --build -d

REM Step 2 – Install Python dependencies
pip install -r client_orchestrator\requirements.txt

REM Step 3 – Run the orchestrator
python client_orchestrator\orchestrator.py
```

---

## Output Files (in results/)

| File | Description |
|------|-------------|
| `mec_results.csv` | Raw RTT data for every task |
| `rtt_comparison.png` | Bar chart: mean RTT edge vs cloud |
| `rtt_scatter.png` | Scatter plot: RTT per task |
| `rtt_boxplot.png` | Box plot: RTT distribution |
| `rtt_timeline.png` | Timeline with rolling average |

---

## How Network Latency Works Here

Because both servers run on your local machine, they normally have
**zero network delay**. To fix this, each container's `start.sh` runs:

```bash
# Edge container (inside Linux container via WSL2)
tc qdisc add dev eth0 root netem delay 5ms 1ms

# Cloud container
tc qdisc add dev eth0 root netem delay 40ms 5ms
```

`tc netem` is Linux Traffic Control – it injects real kernel-level
packet delay. Docker Desktop on Windows uses WSL2 (a real Linux
kernel), so this works perfectly even though you're on Windows.

The `cap_add: NET_ADMIN` in `docker-compose.yml` grants permission
for the container to modify its own network settings.

---

## Tuning Parameters

Edit `client_orchestrator/orchestrator.py`:
- `NUM_TASKS = 60` → how many tasks to simulate
- Task ratio is 50/50 URLLC/eMBB by default (change `generate_task`)

Edit `edge_server/start.sh`:
- `delay 5ms 1ms` → change edge latency

Edit `cloud_server/start.sh`:
- `delay 40ms 5ms` → change cloud latency

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `docker-compose: command not found` | Use `docker compose` (no dash) – newer Docker Desktop |
| Containers start but orchestrator can't connect | Wait 10s more; run orchestrator again |
| `tc: command not found` | Shouldn't happen – iproute2 is in the Dockerfile |
| Graphs not opening | Open PNGs manually from `results\` folder |

---

## Stopping the Project
Double-click **`STOP_PROJECT.bat`** or run:
```cmd
docker-compose down
```
