import streamlit as st
import pandas as pd
import plotly.express as px

st.title("📈 Energy Consumption Analysis")

# Load data
df = pd.read_csv("smart_home_energy_consumption_large.csv")

# Device filter
device = st.selectbox("Select Appliance", df["Appliance Type"].unique())
data = df[df["Appliance Type"] == device]

# ---------------- Trend ----------------
st.subheader("Energy Usage Trend")

fig = px.line(
    data.reset_index(),
    y="Energy Consumption (kWh)",
    title=f"{device} Usage Over Time"
)
st.plotly_chart(fig, use_container_width=True)

# ---------------- Distribution ----------------
st.subheader("Usage Distribution")

fig2 = px.histogram(
    data,
    x="Energy Consumption (kWh)",
    nbins=30,
    title="Energy Distribution"
)
st.plotly_chart(fig2, use_container_width=True)

# ---------------- Device comparison ----------------
st.subheader("Device Comparison")

device_total = df.groupby("Appliance Type")["Energy Consumption (kWh)"].sum()

fig3 = px.bar(
    device_total,
    title="Total Energy by Appliance"
)
st.plotly_chart(fig3, use_container_width=True)

# ---------------- Insights ----------------
st.subheader("Analysis Insights")

highest = device_total.idxmax()
value = device_total.max()

st.warning(f"{highest} consumes highest energy ({value:.2f} kWh).")

avg = df["Energy Consumption (kWh)"].mean()
peak = df["Energy Consumption (kWh)"].max()

if peak > avg * 1.5:
    st.error("High peak usage detected.")
