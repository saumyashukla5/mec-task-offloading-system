

import requests
import time
import random
import csv
import os
import sys
from datetime import datetime

import matplotlib
matplotlib.use('Agg')          
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np


EDGE_URL  = "http://localhost:5001/process"
CLOUD_URL = "http://localhost:5002/process"

HEALTH_EDGE  = "http://localhost:5001/health"
HEALTH_CLOUD = "http://localhost:5002/health"

NUM_TASKS      = 60          # total tasks to generate
RESULTS_DIR    = "results"
CSV_FILENAME   = os.path.join(RESULTS_DIR, "mec_results.csv")
GRAPH_RTT      = os.path.join(RESULTS_DIR, "rtt_comparison.png")
GRAPH_SCATTER  = os.path.join(RESULTS_DIR, "rtt_scatter.png")
GRAPH_BOX      = os.path.join(RESULTS_DIR, "rtt_boxplot.png")
GRAPH_TIMELINE = os.path.join(RESULTS_DIR, "rtt_timeline.png")


TASK_TYPES = {
    "URLLC": {
        "description": "Ultra-Reliable Low Latency (time-critical)",
        "server":      "edge",
        "url":         EDGE_URL,
        "payload_kb_range": (1, 10),      
    },
    "eMBB": {
        "description": "Enhanced Mobile Broadband (throughput-heavy)",
        "server":      "cloud",
        "url":         CLOUD_URL,
        "payload_kb_range": (100, 500),   
    },
}

COLOURS = {
    "URLLC": "#00C4FF",   
    "eMBB":  "#FF6B35",   
}


def wait_for_servers(timeout=60):
    """Poll /health until both servers respond."""
    print("\n[ORCHESTRATOR] Waiting for servers to be ready ...")
    deadline = time.time() + timeout
    for label, url in [("Edge", HEALTH_EDGE), ("Cloud", HEALTH_CLOUD)]:
        while time.time() < deadline:
            try:
                r = requests.get(url, timeout=3)
                if r.status_code == 200:
                    print(f"  ✓ {label} server is UP  ({url})")
                    break
            except Exception:
                pass
            time.sleep(2)
        else:
            print(f"  ✗ {label} server did NOT respond within {timeout}s. "
                  "Make sure Docker containers are running.")
            sys.exit(1)
    print("[ORCHESTRATOR] All servers ready.\n")


def generate_task(task_id: int) -> dict:
    """Return a randomly chosen task dict."""
    task_type = random.choice(list(TASK_TYPES.keys()))
    cfg       = TASK_TYPES[task_type]
    payload   = random.randint(*cfg["payload_kb_range"])
    return {
        "task_id":      f"T{task_id:04d}",
        "task_type":    task_type,
        "payload_size": payload,
        "target_url":   cfg["url"],
        "server_label": cfg["server"],
    }


def send_task(task: dict) -> dict | None:
    """Send the task, measure RTT, return result dict or None on error."""
    payload = {
        "task_id":      task["task_id"],
        "task_type":    task["task_type"],
        "payload_size": task["payload_size"],
    }
    try:
        t_start = time.perf_counter()
        resp    = requests.post(task["target_url"], json=payload, timeout=10)
        t_end   = time.perf_counter()

        rtt_ms  = (t_end - t_start) * 1000   # convert to milliseconds
        data    = resp.json()

        return {
            "task_id":      task["task_id"],
            "task_type":    task["task_type"],
            "payload_kb":   task["payload_size"],
            "server":       data.get("server", task["server_label"]),
            "rtt_ms":       round(rtt_ms, 3),
            "status":       data.get("status", "unknown"),
            "timestamp":    datetime.now().isoformat(),
        }
    except requests.exceptions.RequestException as e:
        print(f"  [ERROR] Task {task['task_id']} failed: {e}")
        return None



def run_simulation() -> list[dict]:
    os.makedirs(RESULTS_DIR, exist_ok=True)
    wait_for_servers()

    results = []
    print(f"[ORCHESTRATOR] Generating {NUM_TASKS} tasks ...\n")
    print(f"{'ID':<8} {'Type':<8} {'Payload':>10} {'Server':<18} {'RTT (ms)':>10}")
    print("─" * 60)

    for i in range(1, NUM_TASKS + 1):
        task   = generate_task(i)
        result = send_task(task)

        if result:
            results.append(result)
            colour = "\033[96m" if result["task_type"] == "URLLC" else "\033[93m"
            reset  = "\033[0m"
            print(f"{result['task_id']:<8} "
                  f"{colour}{result['task_type']:<8}{reset} "
                  f"{result['payload_kb']:>8} KB  "
                  f"{result['server']:<18} "
                  f"{result['rtt_ms']:>9.1f} ms")

 
        time.sleep(random.uniform(0.05, 0.15))

    return results

def save_csv(results: list[dict]):
    if not results:
        return
    fieldnames = list(results[0].keys())
    with open(CSV_FILENAME, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    print(f"\n[LOG] Results saved → {CSV_FILENAME}")


def compute_stats(results: list[dict]) -> dict:
    groups = {}
    for r in results:
        groups.setdefault(r["task_type"], []).append(r["rtt_ms"])

    stats = {}
    for ttype, rtts in groups.items():
        a = np.array(rtts)
        stats[ttype] = {
            "count":  len(a),
            "mean":   np.mean(a),
            "median": np.median(a),
            "std":    np.std(a),
            "min":    np.min(a),
            "max":    np.max(a),
            "p95":    np.percentile(a, 95),
            "rtts":   a,
        }
    return stats


def plot_bar(stats: dict):
    fig, ax = plt.subplots(figsize=(8, 5))
    fig.patch.set_facecolor("#0D1117")
    ax.set_facecolor("#161B22")

    labels = list(stats.keys())
    means  = [stats[t]["mean"]   for t in labels]
    stds   = [stats[t]["std"]    for t in labels]
    colors = [COLOURS[t]         for t in labels]

    bars = ax.bar(labels, means, color=colors, width=0.45,
                  yerr=stds, capsize=8, error_kw={"color": "white", "lw": 2})

    for bar, mean, std in zip(bars, means, stds):
        ax.text(bar.get_x() + bar.get_width()/2, mean + std + 1,
                f"{mean:.1f} ms", ha="center", va="bottom",
                color="white", fontsize=12, fontweight="bold")

    ax.set_title("Mean RTT: MEC Edge vs Core Cloud",
                 color="white", fontsize=15, fontweight="bold", pad=15)
    ax.set_ylabel("Round-Trip Time (ms)", color="#AAAAAA", fontsize=12)
    ax.tick_params(colors="white", labelsize=12)
    ax.spines[:].set_color("#30363D")
    ax.yaxis.grid(True, color="#30363D", linestyle="--", alpha=0.6)
    ax.set_ylim(0, max(means) * 1.4)

    fig.tight_layout()
    fig.savefig(GRAPH_RTT, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"[GRAPH] Saved → {GRAPH_RTT}")

def plot_scatter(results: list[dict]):
    fig, ax = plt.subplots(figsize=(12, 5))
    fig.patch.set_facecolor("#0D1117")
    ax.set_facecolor("#161B22")

    for ttype, colour in COLOURS.items():
        idxs = [i for i, r in enumerate(results) if r["task_type"] == ttype]
        rtts = [results[i]["rtt_ms"] for i in idxs]
        ax.scatter(idxs, rtts, c=colour, s=60, alpha=0.85,
                   label=ttype, zorder=3)

    ax.set_title("RTT per Task (Scatter) – Coloured by Task Type",
                 color="white", fontsize=14, fontweight="bold", pad=12)
    ax.set_xlabel("Task Sequence Number", color="#AAAAAA", fontsize=11)
    ax.set_ylabel("RTT (ms)",             color="#AAAAAA", fontsize=11)
    ax.tick_params(colors="white")
    ax.spines[:].set_color("#30363D")
    ax.yaxis.grid(True, color="#30363D", linestyle="--", alpha=0.5)

    patches = [mpatches.Patch(color=COLOURS[t], label=t) for t in COLOURS]
    ax.legend(handles=patches, facecolor="#0D1117", labelcolor="white",
              edgecolor="#30363D", fontsize=11)

    fig.tight_layout()
    fig.savefig(GRAPH_SCATTER, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"[GRAPH] Saved → {GRAPH_SCATTER}")


def plot_boxplot(stats: dict):
    fig, ax = plt.subplots(figsize=(8, 5))
    fig.patch.set_facecolor("#0D1117")
    ax.set_facecolor("#161B22")

    labels = list(stats.keys())
    data   = [stats[t]["rtts"] for t in labels]
    colors = [COLOURS[t]       for t in labels]

    bp = ax.boxplot(data, patch_artist=True, labels=labels,
                    medianprops={"color": "white", "lw": 2},
                    whiskerprops={"color": "#AAAAAA"},
                    capprops={"color": "#AAAAAA"},
                    flierprops={"marker": "o", "markerfacecolor": "#FF4444",
                                "markersize": 5})

    for patch, colour in zip(bp["boxes"], colors):
        patch.set_facecolor(colour)
        patch.set_alpha(0.7)

    ax.set_title("RTT Distribution (Box Plot)",
                 color="white", fontsize=14, fontweight="bold", pad=12)
    ax.set_ylabel("RTT (ms)", color="#AAAAAA", fontsize=12)
    ax.tick_params(colors="white", labelsize=12)
    ax.spines[:].set_color("#30363D")
    ax.yaxis.grid(True, color="#30363D", linestyle="--", alpha=0.5)

    fig.tight_layout()
    fig.savefig(GRAPH_BOX, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"[GRAPH] Saved → {GRAPH_BOX}")

def plot_timeline(results: list[dict]):
    fig, ax = plt.subplots(figsize=(12, 5))
    fig.patch.set_facecolor("#0D1117")
    ax.set_facecolor("#161B22")

    for ttype, colour in COLOURS.items():
        subset = [(i, r["rtt_ms"]) for i, r in enumerate(results)
                  if r["task_type"] == ttype]
        if not subset:
            continue
        xs, ys = zip(*subset)
        ax.plot(xs, ys, "o-", color=colour, alpha=0.5, ms=4, lw=1.2,
                label=f"{ttype} raw")

  
        ys_arr = np.array(ys)
        xs_arr = np.array(xs)
        if len(ys_arr) >= 5:
            roll = np.convolve(ys_arr, np.ones(5)/5, mode="valid")
            ax.plot(xs_arr[4:], roll, color=colour, lw=2.5,
                    label=f"{ttype} avg (5)")

    ax.set_title("RTT Timeline with Rolling Average",
                 color="white", fontsize=14, fontweight="bold", pad=12)
    ax.set_xlabel("Task Sequence", color="#AAAAAA", fontsize=11)
    ax.set_ylabel("RTT (ms)",      color="#AAAAAA", fontsize=11)
    ax.tick_params(colors="white")
    ax.spines[:].set_color("#30363D")
    ax.yaxis.grid(True, color="#30363D", linestyle="--", alpha=0.5)
    ax.legend(facecolor="#0D1117", labelcolor="white",
              edgecolor="#30363D", fontsize=10)

    fig.tight_layout()
    fig.savefig(GRAPH_TIMELINE, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"[GRAPH] Saved → {GRAPH_TIMELINE}")


def print_summary(stats: dict):
    print("\n" + "═"*60)
    print("  SIMULATION SUMMARY")
    print("═"*60)
    for ttype, s in stats.items():
        server = "MEC Edge (5G)" if ttype == "URLLC" else "Core Cloud"
        print(f"\n  {ttype}  →  {server}")
        print(f"    Tasks  : {s['count']}")
        print(f"    Mean   : {s['mean']:.2f} ms")
        print(f"    Median : {s['median']:.2f} ms")
        print(f"    Std    : {s['std']:.2f} ms")
        print(f"    Min    : {s['min']:.2f} ms")
        print(f"    Max    : {s['max']:.2f} ms")
        print(f"    P95    : {s['p95']:.2f} ms")
    print("\n" + "═"*60)



if __name__ == "__main__":
    results = run_simulation()

    if not results:
        print("[ERROR] No results collected. Exiting.")
        sys.exit(1)

    save_csv(results)

    stats = compute_stats(results)
    print_summary(stats)

    print("\n[GRAPHS] Generating visualizations ...")
    plot_bar(stats)
    plot_scatter(results)
    plot_boxplot(stats)
    plot_timeline(results)

    print("\n[DONE] Open the 'results/' folder to see your CSV and graphs.")
