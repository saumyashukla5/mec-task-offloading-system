import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")

st.title("MEC Task Offloading Dashboard")

df = pd.read_csv("results.csv")
summary = pd.read_csv("summary.csv")

st.subheader("Task Offloading Decisions")
st.dataframe(df)

cloud_avg = summary["CloudAvg"][0]
mec_avg = summary["MECAvg"][0]
reduction = summary["Reduction"][0]

st.subheader("Latency Comparison")

col1, col2, col3 = st.columns(3)
col1.metric("Cloud Latency", f"{cloud_avg:.4f}")
col2.metric("MEC Latency", f"{mec_avg:.4f}")
col3.metric("Reduction (%)", f"{reduction:.2f}%")

fig, ax = plt.subplots()
ax.bar(["Cloud Only", "MEC"], [cloud_avg, mec_avg])
ax.set_ylabel("RTT")
st.pyplot(fig)

st.subheader("Edge vs Cloud (MEC System)")

edge = df[df["Server"] == "Edge"]
cloud = df[df["Server"] == "Cloud"]

fig2, ax2 = plt.subplots()
ax2.boxplot([edge["RTT"], cloud["RTT"]], tick_labels=["Edge", "Cloud"])
st.pyplot(fig2)

st.subheader("Latency Breakdown")

fig3, ax3 = plt.subplots()
ax3.bar(
    ["Network", "Processing", "Total"],
    [
        df["NetworkDelay"].mean(),
        df["ProcessingTime"].mean(),
        df["RTT"].mean()
    ]
)
st.pyplot(fig3)

st.subheader("Task Distribution")
st.bar_chart(df["Server"].value_counts())

st.subheader("Latency Over Time")
st.line_chart(df["RTT"])