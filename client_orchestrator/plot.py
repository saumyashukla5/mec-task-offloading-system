import pandas as pd
import matplotlib.pyplot as plt

print("🔥 Running Advanced MEC Analysis")

df = pd.read_csv("results.csv")

edge = df[df["Server"] == "Edge"]
cloud = df[df["Server"] == "Cloud"]

edge_avg = edge["RTT"].mean()
cloud_avg = cloud["RTT"].mean()

improvement = ((cloud_avg - edge_avg) / cloud_avg) * 100


print("\n===== FINAL ANALYSIS =====")
print(f"Edge Avg Latency  : {edge_avg:.4f} sec")
print(f"Cloud Avg Latency : {cloud_avg:.4f} sec")
print(f"🚀 Latency Reduction: {improvement:.2f}%")


plt.figure()
plt.bar(["Edge", "Cloud"], [edge_avg, cloud_avg])
plt.title("Average Latency Comparison (MEC vs Cloud)")
plt.ylabel("RTT (seconds)")
plt.show()


plt.figure()
plt.boxplot([edge["RTT"], cloud["RTT"]], labels=["Edge", "Cloud"])
plt.title("Latency Distribution (Edge vs Cloud)")
plt.ylabel("RTT (seconds)")
plt.show()