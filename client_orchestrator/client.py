import requests
import time
import random
import csv
import threading

EDGE_URL = "http://localhost:5001/process"
CLOUD_URL = "http://localhost:5002/process"

NUM_USERS = 5
TASKS_PER_USER = 30

cloud_results = []
mec_results = []
detailed_results = []

def cloud_only_simulation():
    for i in range(NUM_USERS * TASKS_PER_USER):
        network_delay = random.uniform(0.005, 0.02)
        start = time.time()
      
        response = requests.post(CLOUD_URL, json={"task": "eMBB"})
        processing_time = response.elapsed.total_seconds()
        end = time.time()
        rtt = end - start
        cloud_results.append(rtt)

def generate_task():
    return random.choice(["URLLC", "eMBB"])

def simulate_user(user_id):
    for i in range(TASKS_PER_USER):
        task = generate_task()
        data_size = random.randint(100, 1000)
        network_delay = random.uniform(0.005, 0.02)

        if task == "URLLC":
            server = "Edge"
            url = EDGE_URL
            reason = "URLLC Edge"
        elif data_size > 700:
            server = "Cloud"
            url = CLOUD_URL
            reason = "Large Data Cloud"
        else:
            if network_delay < 0.01:
                server = "Edge"
                url = EDGE_URL
                reason = "Low Delay Edge"
            else:
                server = "Cloud"
                url = CLOUD_URL
                reason = "High Delay Cloud"

        start = time.time()
        time.sleep(network_delay)
        response = requests.post(url, json={"task": task})
        processing_time = response.elapsed.total_seconds()
        end = time.time()
        rtt = end - start

        mec_results.append(rtt)

        detailed_results.append([
            user_id,
            task,
            data_size,
            server,
            network_delay,
            processing_time,
            rtt,
            reason
        ])

def mec_simulation():
    threads = []
    for user_id in range(NUM_USERS):
        t = threading.Thread(target=simulate_user, args=(user_id,))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()

cloud_only_simulation()
mec_simulation()

avg_cloud = sum(cloud_results) / len(cloud_results)
avg_mec = sum(mec_results) / len(mec_results)

reduction = ((avg_cloud - avg_mec) / avg_cloud) * 100

with open("results.csv", "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow([
        "User",
        "Task",
        "DataSize",
        "Server",
        "NetworkDelay",
        "ProcessingTime",
        "RTT",
        "DecisionReason"
    ])
    writer.writerows(detailed_results)

with open("summary.csv", "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["CloudAvg", "MECAvg", "Reduction"])
    writer.writerow([avg_cloud, avg_mec, reduction])